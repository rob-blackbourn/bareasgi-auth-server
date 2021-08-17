"""
Auth repository
"""

from .authentication_repository import AuthenticationRepository
from .authorization_repository import AuthorizationRepository

class AuthRepository:
    """Auth repository"""

    def __init__(
            self,
            authentication_repository: AuthenticationRepository,
            authorization_repository: AuthorizationRepository
    ) -> None:
        self.authentication_repository = authentication_repository
        self.authorization_repository = authorization_repository

    async def initialise(self) -> None:
        """Initialise"""
        await self.authentication_repository.initialise()
        await self.authorization_repository.initialise()
