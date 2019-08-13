"""
Authentication Service
"""

from ..authentication_repository import AuthenticationRepository
from .authentication_service import AuthenticationService


class RepositoryAuthenticationService(AuthenticationService):
    """Repository Authentication service"""

    def __init__(
            self, authentication_repository: AuthenticationRepository
    ) -> None:
        """Initialise the authentication service

        :param authentication_repository: The authentication provider
        :type authentication_repository: AuthProvider
        """
        self.authentication_repository = authentication_repository
        self._is_initialised = False

    async def is_password_for_user(self, name: str, password: str) -> bool:
        """Return true if the password is valid for this user

        :param name: The user's name
        :type name: str
        :param password: The users password in clear text
        :type password: str
        :return: True if the password is correct, otherwise false
        :rtype: bool
        """
        await self._initialise()
        pwd = await self.authentication_repository.read(name)
        return pwd.is_valid_password(password)


    async def is_valid(self, email: str) -> bool:
        """Return true if the user's email is valid

        :param email: The user's email
        :type email: str
        :return: True if the email is valid, otherwise false.
        :rtype: bool
        """
        await self._initialise()
        pwd = await self.authentication_repository.read(email)
        return pwd is not None and pwd.state == 'active'

    async def _initialise(self):
        if self._is_initialised:
            return
        await self.authentication_repository.initialise()
