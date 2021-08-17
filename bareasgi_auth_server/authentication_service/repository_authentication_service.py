"""
Authentication Service
"""

from typing import Any, Mapping, Optional

from ..auth_repository import AuthRepository
from .authentication_service import AuthenticationService


class RepositoryAuthenticationService(AuthenticationService):
    """Repository Authentication service"""

    def __init__(
            self, auth_repository: AuthRepository
    ) -> None:
        self.auth_repository = auth_repository
        self._is_initialised = False

    async def authenticate(self, **credentials) -> Optional[str]:
        username = credentials['username']
        password = credentials['password']
        await self._initialise()
        pwd = await self.auth_repository.authentication_repository.read(username)
        return username if pwd and pwd.is_valid_password(password) else None

    async def is_valid_user(self, user_id: str) -> bool:
        await self._initialise()
        pwd = await self.auth_repository.authentication_repository.read(user_id)
        return pwd is not None and pwd.state == 'active'

    async def authorizations(self, user_id: str) -> Mapping[str, Any]:
        roles = await self.auth_repository.authorization_repository.roles(user_id)
        return {
            'roles': roles
        }

    async def _initialise(self):
        if self._is_initialised:
            return
        await self.auth_repository.initialise()
