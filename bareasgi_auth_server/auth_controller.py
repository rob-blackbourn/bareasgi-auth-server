"""Authentication Controller
"""

from datetime import datetime, timedelta
import logging
from typing import Dict, List
from urllib.error import HTTPError
from urllib.parse import parse_qsl, urlparse

from bareasgi import (
    Application,
    text_reader,
    json_response
)
import bareutils.header as header
from bareutils import response_code
from bareutils.cookies import make_cookie
from baretypes import (
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpResponse,
    Header
)
from bareasgi_auth_common import (
    JwtAuthenticator,
    TokenManager,
    ForbiddenError,
    UnauthorisedError,
    TokenStatus
)
import jwt

from .auth_service import AuthService
from .types import BadRequestError

LOGGER = logging.getLogger(__name__)


class AuthController:
    """Authentication and authorization controller"""

    def __init__(
            self,
            path_prefix: str,
            authenticator: JwtAuthenticator,
            auth_service: AuthService
    ) -> None:
        """Initialise the authentication controller.

        Args:
            path_prefix (str): The path prefix.
            authenticator (JwtAuthenticator): [description]
            auth_service (AuthService): [description]
        """
        self.path_prefix = path_prefix
        self.authenticator = authenticator
        self.auth_service = auth_service

    def add_routes(self, app: Application) -> Application:
        """Add the routes that are handled by the controller.

        Args:
            app (Application): The ASGI application.

        Returns:
            Application: The ASGI application for chaining.
        """

        app.http_router.add(
            {'POST', 'OPTIONS'},
            self.path_prefix + '/login',
            self.login_redirect
        )
        app.http_router.add(
            {'POST', 'OPTIONS'},
            self.path_prefix + '/authenticate',
            self.login
        )
        app.http_router.add(
            {'POST', 'OPTIONS'},
            self.path_prefix + '/logout',
            self.logout
        )
        app.http_router.add(
            {'POST'},
            self.path_prefix + '/renew_token',
            self.renew_token
        )
        app.http_router.add(
            {'GET'},
            self.path_prefix + '/whoami',
            self.who_am_i
        )

        return app

    async def _authenticate(
            self,
            scope: Scope,
            content: Content
    ) -> bytes:
        content_type = header.content_type(scope['headers'])
        media_type = None if content_type is None else content_type[0]
        if media_type != 'application/x-www-form-urlencoded':
            raise BadRequestError(
                scope,
                'Expected content-type to be application/x-www-form-urlencoded'
            )

        credentials = dict(parse_qsl(await text_reader(content)))

        user_id = await self.auth_service.authenticate(**credentials)

        if user_id is None:
            raise ForbiddenError(scope, 'Invalid credentials')

        LOGGER.info('Authenticated: %s', user_id)

        authorizations = await self.auth_service.authorizations(user_id)

        now = datetime.utcnow()
        token = self.authenticator.token_manager.encode(
            user_id,
            now,
            now,
            None,
            authorizations=authorizations
        )

        return token

    @classmethod
    def _get_redirect(cls, scope: Scope) -> bytes:
        query: Dict[bytes, bytes] = dict(parse_qsl(scope['query_string']))

        # Get the location where the browser will be redirected to if authentication is successful from the query string.
        redirect = query.get(b'redirect')
        if not redirect:
            LOGGER.warning('The login request had no redirect')
            raise BadRequestError(scope, 'No redirect')
        urlparts = urlparse(redirect)
        if urlparts.scheme is None or not urlparts.scheme:
            LOGGER.warning(
                'The redirect URL has no scheme: "%s"',
                redirect
            )
            raise BadRequestError(scope, 'Malformed redirect - no scheme')

        return redirect

    async def login_redirect(
            self,
            scope: Scope,
            _info: Info,
            _matches: RouteMatches,
            content: Content
    ) -> HttpResponse:
        redirect = self._get_redirect(scope)
        token = await self._authenticate(scope, content)
        cookie = self.authenticator.token_manager.make_cookie(token)

        LOGGER.debug('Sending token: %s', token)

        headers = [
            (b'set-cookie', cookie),
            (b'location', redirect)
        ]

        return response_code.FOUND, headers

    async def login(
            self,
            scope: Scope,
            _info: Info,
            _matches: RouteMatches,
            content: Content
    ) -> HttpResponse:
        token = await self._authenticate(scope, content)
        cookie = self.authenticator.token_manager.make_cookie(token)

        LOGGER.debug('Sending token: %s', token)

        headers: List[Header] = [
            (b'set-cookie', cookie)
        ]

        return response_code.FOUND, headers

    async def logout(
            self,
            _scope: Scope,
            _info: Info,
            __matches: RouteMatches,
            _content: Content
    ) -> HttpResponse:
        set_cookie = make_cookie(
            self.authenticator.token_manager.cookie_name,
            b'',
            expires=timedelta(seconds=0),
            domain=self.authenticator.token_manager.domain,
            path=self.authenticator.token_manager.path,
            http_only=True
        )
        return response_code.NO_CONTENT, [(b'set-cookie', set_cookie)]

    async def who_am_i(
            self,
            scope: Scope,
            _info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> HttpResponse:
        try:
            token = self.authenticator.token_manager.get_token_from_headers(
                scope['headers'])

            token_status = self.authenticator.get_token_status(token)

            if token_status == TokenStatus.EXPIRED:
                token = await self._renew_token(scope)

            if token is None:
                raise UnauthorisedError(
                    scope,
                    'Client requires authentication'
                )

            payload = self.authenticator.token_manager.decode(token)

            return json_response(response_code.OK, None, {'username': payload['sub']})

        except HTTPError:
            raise

        except (jwt.exceptions.ExpiredSignature, PermissionError):
            LOGGER.exception('JWT encoding failed')
            return response_code.UNAUTHORIZED

        except:  # pylint: disable=bare-except
            LOGGER.exception('Failed to re-sign the token')
            return response_code.INTERNAL_SERVER_ERROR

    async def _renew_token(self, scope: Scope) -> bytes:
        token = self.authenticator.token_manager.get_token_from_headers(
            scope['headers'])
        if token is None:
            raise UnauthorisedError(scope, 'authentication required')

        payload = self.authenticator.token_manager.decode(token)

        user_id = payload['sub']
        issued_at = payload['iat']

        LOGGER.info(
            'Token renewal request for user "%s" for token issued at %s.',
            user_id,
            issued_at
        )

        now = datetime.utcnow()

        login_expiry = issued_at + self.authenticator.token_manager.session_expiry
        if now > login_expiry:
            LOGGER.info(
                'Token too old for user "%s" issued at "%s" expired at "%s"',
                user_id,
                issued_at,
                login_expiry
            )
            raise UnauthorisedError(scope, 'login expired')

        if not await self.auth_service.is_valid_user(user_id):
            LOGGER.warning(
                'User "%s" is no longer valid',
                user_id
            )
            raise ForbiddenError(scope, 'invalid user')

        authorizations = await self.auth_service.authorizations(user_id)

        # Renew the token keeping the "issued at" timestamp to ensure
        # reauthentication.
        token = self.authenticator.token_manager.encode(
            user_id,
            now,
            issued_at,
            None,
            authorizations=authorizations
        )

        LOGGER.info(
            'Token renewed for user "%s" will expire at %s',
            user_id,
            login_expiry
        )

        return token

    async def renew_token(
            self,
            scope: Scope,
            _info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> HttpResponse:
        try:
            token = await self._renew_token(scope)

            set_cookie = self.authenticator.token_manager.make_cookie(token)

            return response_code.NO_CONTENT, [(b'set-cookie', set_cookie)]

        except HTTPError:
            raise

        except:  # pylint: disable=bare-except
            LOGGER.exception('Failed to renew token')
            return response_code.INTERNAL_SERVER_ERROR
