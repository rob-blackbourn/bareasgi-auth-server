"""Authentication Controller
"""

from datetime import datetime, timedelta
import json
import logging
from typing import Dict, Optional
from urllib.parse import parse_qsl, urlparse

from bareasgi import (
    Application,
    text_reader,
    text_writer,
    HttpRequest,
    HttpResponse
)
from bareutils import header, response_code
from bareutils.cookies import make_cookie
from bareasgi_auth_common import (
    TokenManager,
    ForbiddenError,
    UnauthorizedError,
    TokenStatus,
    BareASGIError
)
import jwt

from .auth_service import AuthService
from .types import (
    BadRequestError,
    UserInvalidError,
    UserCredentialsError,
    UserNotFoundError
)
from .utils import JSONEncoderEx

LOGGER = logging.getLogger(__name__)


class AuthController:
    """Authentication and authorization controller"""

    def __init__(
            self,
            path_prefix: str,
            token_manager: TokenManager,
            auth_service: AuthService
    ) -> None:
        """Initialise the authentication controller.

        Args:
            path_prefix (str): The path prefix.
            authenticator (JwtAuthenticator): [description]
            auth_service (AuthService): [description]
        """
        self.path_prefix = path_prefix
        self.token_manager = token_manager
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

    async def _authenticate(self, request: HttpRequest) -> bytes:
        content_type = header.content_type(request.scope['headers'])
        media_type = None if content_type is None else content_type[0]
        if media_type != b'application/x-www-form-urlencoded':
            LOGGER.debug('Invalid media type: %s', media_type)
            raise BadRequestError(
                request,
                'Expected content-type to be application/x-www-form-urlencoded'
            )

        credentials = dict(parse_qsl(await text_reader(request.body)))

        try:
            LOGGER.debug('Authenticating')
            user_id = await self.auth_service.authenticate(**credentials)
        except (UserNotFoundError, UserCredentialsError) as error:
            LOGGER.info('Authentication failed')
            raise UnauthorizedError(request, 'Invalid credentials') from error
        except UserInvalidError as error:
            LOGGER.warning('User invalid')
            raise ForbiddenError(request, 'Invalid user') from error

        LOGGER.info('Authenticated: %s', user_id)

        authorizations = await self.auth_service.authorizations(user_id)

        now = datetime.utcnow()
        token = self.token_manager.encode(
            user_id,
            now,
            now,
            None,
            authorizations=authorizations
        )

        return token

    @classmethod
    def _get_redirect(cls, request: HttpRequest) -> Optional[bytes]:
        query: Dict[bytes, bytes] = dict(
            parse_qsl(request.scope['query_string'])
        )

        # Get the location where the browser will be redirected to if authentication is successful from the query string.
        redirect = query.get(b'redirect')
        if redirect is not None:
            # Check it's valid
            urlparts = urlparse(redirect)
            if urlparts.scheme is None or not urlparts.scheme:
                LOGGER.warning(
                    'The redirect URL has no scheme: "%s"',
                    redirect
                )
                raise BadRequestError(
                    request,
                    'Malformed redirect - no scheme'
                )

        return redirect

    async def login_redirect(self, request: HttpRequest) -> HttpResponse:
        LOGGER.debug('Handling a login redirect')

        try:
            token = await self._authenticate(request)
            cookie = self.token_manager.make_cookie(token)

            headers = [
                (b'set-cookie', cookie)
            ]

            redirect = self._get_redirect(request)
            if redirect is not None:
                headers.append(
                    (b'location', redirect)
                )

            LOGGER.debug('Sending token: %s', token)

            return HttpResponse(response_code.FOUND, headers)

        except BareASGIError as error:

            LOGGER.warning('Failed to authenticate: %s', error.message)
            return HttpResponse(
                error.status,
                error.headers,
                text_writer(error.message) if error.message else None
            )

        except:  # pylint: disable=bare-except

            LOGGER.exception('Failed to authenticate')
            return HttpResponse(response_code.INTERNAL_SERVER_ERROR)

    async def login(self, request: HttpRequest) -> HttpResponse:
        LOGGER.debug('Handling login')

        try:
            LOGGER.debug('Authenticating')

            token = await self._authenticate(request)
            cookie = self.token_manager.make_cookie(token)

            LOGGER.debug('Sending token: %s', token)

            headers = [
                (b'set-cookie', cookie)
            ]

            return HttpResponse(response_code.FOUND, headers)

        except BareASGIError as error:

            LOGGER.warning('Failed to authenticate: %s', error.message)

            return HttpResponse(
                error.status,
                error.headers,
                text_writer(error.message) if error.message else None
            )

        except:  # pylint: disable=bare-except

            LOGGER.exception('Failed to authenticate')

            return HttpResponse(response_code.INTERNAL_SERVER_ERROR)

    async def logout(self, _request: HttpRequest) -> HttpResponse:
        LOGGER.debug("Handling logout request")

        set_cookie = make_cookie(
            self.token_manager.cookie_name,
            b'',
            expires=timedelta(seconds=0),
            domain=self.token_manager.domain,
            path=self.token_manager.path,
            http_only=True
        )
        headers = [
            (b'set-cookie', set_cookie)
        ]
        return HttpResponse(response_code.NO_CONTENT, headers)

    async def who_am_i(self, request: HttpRequest) -> HttpResponse:
        LOGGER.debug("Handling whoami request")

        try:
            token = self.token_manager.get_token_from_headers(request)
            token_status = self.token_manager.get_token_status(token)
            if token is None or token_status == TokenStatus.MISSING:
                LOGGER.debug('No token found')
                raise UnauthorizedError(
                    request,
                    'Client requires authentication'
                )
            elif token_status == TokenStatus.EXPIRED:
                LOGGER.debug('Token expired')
                token = await self._renew_token(request)

            payload = self.token_manager.decode(token)
            body = text_writer(json.dumps(payload, cls=JSONEncoderEx))

            LOGGER.debug("Sending JWT payload: %s", payload)

            return HttpResponse(response_code.OK, None, body)

        except BareASGIError as error:
            return HttpResponse(
                error.status,
                error.headers,
                text_writer(error.message) if error.message else None
            )

        except (jwt.exceptions.ExpiredSignatureError, PermissionError):
            LOGGER.exception('JWT encoding failed')
            return HttpResponse(response_code.UNAUTHORIZED)

        except:  # pylint: disable=bare-except
            LOGGER.exception('Failed to re-sign the token')
            return HttpResponse(response_code.INTERNAL_SERVER_ERROR)

    async def _renew_token(self, request: HttpRequest) -> bytes:
        LOGGER.debug('Renewing token')

        token = self.token_manager.get_token_from_headers(request)
        if token is None:
            LOGGER.debug('Token not found')
            raise UnauthorizedError(request, 'authentication required')

        payload = self.token_manager.decode(token)

        user_id = payload['sub']
        issued_at = payload['iat']

        LOGGER.info(
            'Token renewal request for user "%s" for token issued at %s.',
            user_id,
            issued_at
        )

        now = datetime.utcnow()

        login_expiry = issued_at + self.token_manager.session_expiry
        if now > login_expiry:
            LOGGER.info(
                'Token too old for user "%s" issued at "%s" expired at "%s"',
                user_id,
                issued_at,
                login_expiry
            )
            raise UnauthorizedError(request, 'login expired')

        if not await self.auth_service.is_valid_user(user_id):
            LOGGER.warning(
                'User "%s" is no longer valid',
                user_id
            )
            raise ForbiddenError(request, 'invalid user')

        authorizations = await self.auth_service.authorizations(user_id)

        # Renew the token keeping the "issued at" timestamp to ensure
        # re-authentication.
        token = self.token_manager.encode(
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

    async def renew_token(self, request: HttpRequest) -> HttpResponse:
        LOGGER.debug('Handling renew-token request')

        try:
            token = await self._renew_token(request)

            set_cookie = self.token_manager.make_cookie(token)
            headers = [
                (b'set-cookie', set_cookie)
            ]

            return HttpResponse(response_code.NO_CONTENT, headers)

        except BareASGIError as error:
            return HttpResponse(
                error.status,
                error.headers,
                text_writer(error.message) if error.message else None
            )

        except:  # pylint: disable=bare-except
            LOGGER.exception('Failed to renew token')
            return HttpResponse(response_code.INTERNAL_SERVER_ERROR)
