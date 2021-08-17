"""Types"""

from baretypes import Scope
import bareutils.response_code as response_code

from bareasgi_auth_common import BareASGIError


class BadRequestError(BareASGIError):

    def __init__(self, scope: Scope, msg: str) -> None:
        super().__init__(
            scope,
            response_code.BAD_REQUEST,
            [(b'content_type', b'text/plain')],
            msg
        )
