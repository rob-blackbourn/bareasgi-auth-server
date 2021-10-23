"""Types"""

from bareasgi import HttpRequest
import bareutils.response_code as response_code

from bareasgi_auth_common import BareASGIError


class BadRequestError(BareASGIError):

    def __init__(self, request: HttpRequest, message: str) -> None:
        super().__init__(
            request,
            response_code.BAD_REQUEST,
            [(b'content_type', b'text/plain')],
            message
        )


class UserNotFoundError(PermissionError):
    pass


class UserCredentialsError(PermissionError):
    pass


class UserInvalidError(PermissionError):
    pass
