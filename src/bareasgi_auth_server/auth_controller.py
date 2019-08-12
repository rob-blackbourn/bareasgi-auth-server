"""Authentication Controller
"""

from datetime import datetime, timedelta
import logging
from typing import Mapping, Any
from urllib.parse import parse_qs, urlparse

from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpResponse,
    text_response,
    text_reader,
    json_response
)
from bareasgi.middleware import mw
import bareutils.header as header
from bareutils import response_code
import bareasgi_jinja2
from bareasgi_auth_common import JwtAuthenticator
from bareasgi_auth_common import TokenManager
import jwt

from .auth_service import AuthService

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)


class AuthController:
    """Authentication controller"""

    def __init__(
            self,
            path_prefix: str,
            login_expiry: timedelta,
            token_manager: TokenManager,
            auth_service: AuthService,
            authenticator: JwtAuthenticator
    ) -> None:
        """Initialise the authentication controller

        :param path_prefix: The prefix to the paths
        :type path_prefix: str
        :param login_expiry: The time before the user is required to re-authenticate
        :type login_expiry: timedelta
        :param token_manager: The token manager
        :type token_manager: TokenManager
        :param auth_service: The authentication service
        :type auth_service: AuthService
        :param authenticator: The authenticator
        :type authenticator: JwtAuthenticator
        """
        self.path_prefix = path_prefix
        self.login_expiry = login_expiry
        self.token_manager = token_manager
        self.auth_service = auth_service
        self.authenticator = authenticator

    def add_routes(self, app: Application) -> Application:
        """Add the routes to the application

        :param app: The application
        :type app: Application
        :return: The application
        :rtype: Application
        """

        app.http_router.add(
            {'GET'},
            self.path_prefix + '/login',
            self.login_view
        )
        app.http_router.add(
            {'POST'},
            self.path_prefix + '/login',
            self.login_post
        )
        app.http_router.add(
            {'POST'},
            self.path_prefix + '/renew_token',
            self.renew_token
        )

        app.http_router.add(
            {'GET'},
            self.path_prefix + '/whoami',
            mw(self.authenticator, handler=self.who_am_i)
        )

        return app

    # pylint: disable=unused-argument
    @bareasgi_jinja2.template('login.html')
    async def login_view(
            self,
            scope: Scope,
            info: Info,
            matches: RouteMatches,
            content: Content
    ) -> Mapping[str, Any]:
        """Displays the login page

        :param scope: The ASGI scope
        :type scope: Scope
        :param info: The application shared info
        :type info: Info
        :param matches: The route matches
        :type matches: RouteMatches
        :param content: The ASGI content
        :type content: Content
        :return: The variables for jinja2 form templating
        :rtype: Mapping[str, Any]
        """
        query_string = scope["query_string"].decode()
        action = f'{self.path_prefix}/login?{query_string}'
        return {
            'action': action,
        }

    # pylint: disable=unused-argument
    async def login_post(
            self,
            scope: Scope,
            info: Info,
            matches: RouteMatches,
            content: Content
    ) -> HttpResponse:
        """A login POST request handler

        :param scope: The ASGI scope
        :type scope: Scope
        :param info: The application shared info
        :type info: Info
        :param matches: The route matches
        :type matches: RouteMatches
        :param content: The ASGI content
        :type content: Content
        :return: A login response
        :rtype: HttpResponse
        """
        try:
            query = parse_qs(scope['query_string'])
            redirect = query.get(b'redirect')
            if not redirect:
                logger.debug('No redirect')
                return text_response(response_code.NOT_FOUND, None, 'No redirect')
            redirect = redirect[0]

            text = await text_reader(content)
            body = parse_qs(text)
            username = body['username'][0]
            password = body['password'][0]

            if not await self.auth_service.is_password_for_user(username, password):
                raise RuntimeError('Invalid username or password')

            now = datetime.utcnow()
            token = self.token_manager.encode(username, now, now)

            logger.debug('Sending token: %s', token)
            urlparts = urlparse(redirect)
            if urlparts.scheme is None or not urlparts.scheme:
                raise RuntimeError('The redirect URL has no scheme')

            set_cookie = self.token_manager.make_cookie(token)

            return response_code.FOUND, [(b'set-cookie', set_cookie), (b'location', redirect)]

        except:  # pylint: disable=bare-except
            logger.exception('Failed to log in')
            location = header.find(b'referer', scope['headers'])
            return response_code.FOUND, [(b'location', location)]

    # pylint: disable=unused-argument
    async def who_am_i(
            self,
            scope: Scope,
            info: Info,
            matches: RouteMatches,
            content: Content
    ) -> HttpResponse:
        """Returns the login status of the user

        :param scope: The ASGI scope
        :type scope: Scope
        :param info: The application shared info
        :type info: Info
        :param matches: The route matches
        :type matches: RouteMatches
        :param content: The ASGI content
        :type content: Content
        :return: A whoami response
        :rtype: HttpResponse
        """
        try:
            token = self.token_manager.get_token_from_headers(scope['headers'])
            if token is None:
                return text_response(
                    response_code.UNAUTHORIZED,
                    None,
                    'Client requires authentication'
                )

            payload = self.token_manager.decode(token)

            return json_response(response_code.OK, None, {'username': payload['sub']})
        except (jwt.exceptions.ExpiredSignature, PermissionError):
            logger.exception('JWT encoding failed')
            return response_code.UNAUTHORIZED
        except:  # pylint: disable=bare-except
            logger.exception('Failed to re-sign the token')
            return response_code.INTERNAL_SERVER_ERROR

    # pylint: disable=unused-argument
    async def renew_token(
            self,
            scope: Scope,
            info: Info,
            matches: RouteMatches,
            content: Content
    ) -> HttpResponse:
        """Renew the token

        :param scope: The ASGI scope
        :type scope: Scope
        :param info: The application shared info
        :type info: Info
        :param matches: The route matches
        :type matches: RouteMatches
        :param content: The ASGI content
        :type content: Content
        :return: A no-content response with the cookie in the header.
        :rtype: HttpResponse
        """
        try:
            token = self.token_manager.get_token_from_headers(scope['headers'])
            if not token:
                return text_response(
                    response_code.UNAUTHORIZED,
                    None,
                    'Client requires authentication'
                )

            payload = self.token_manager.decode(token)

            user = payload['sub']
            issued_at = payload['iat']

            logger.debug(
                'Token renewal request: user=%s, iat=%s',
                user,
                issued_at
            )

            utc_now = datetime.utcnow()

            authentication_expiry = issued_at + self.login_expiry
            if utc_now > authentication_expiry:
                logger.debug(
                    'Token expired for user %s issued at %s expired at %s',
                    user,
                    issued_at,
                    authentication_expiry
                )
                return text_response(response_code.UNAUTHORIZED, None, 'Authentication expired')

            if not self.auth_service.is_valid(user):
                return response_code.FORBIDDEN, None, None

            logger.debug('Token renewed for %s', user)
            token = self.token_manager.encode(user, utc_now, issued_at)
            logger.debug('Sending token %s', token)

            set_cookie = self.token_manager.make_cookie(token)

            return response_code.NO_CONTENT, [(b'set-cookie', set_cookie)], None

        except:  # pylint: disable=bare-except
            logger.exception('Failed to renew token')
            return response_code.INTERNAL_SERVER_ERROR, None, None
