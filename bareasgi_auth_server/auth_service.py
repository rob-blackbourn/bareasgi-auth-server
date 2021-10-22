"""
Authentication Service
"""

from abc import ABCMeta, abstractmethod
from typing import List


class AuthService(metaclass=ABCMeta):
    """A base class for authentication services"""

    @abstractmethod
    async def authenticate(self, **credentials) -> str:
        """Authenticate the user.

        Raises:
            UserUnknownError: When the user is not known.
            UserCredentialsError: For bad credentials.
            UserInvalidError: When the user is not valid.

        Returns:
            str: The user identifier.
        """

    @abstractmethod
    async def is_valid_user(self, user_id: str) -> bool:
        """Check the user is still valid

        Args:
            user_id (str): The user identifier.

        Returns:
            bool: True if the user is valid otherwise false.
        """

    @abstractmethod
    async def authorizations(self, user_id: str) -> List[str]:
        """Return the authorizations for the user.

        Args:
            user_id (str): The used identifier.

        Returns:
            List[str]: The authorizations.
        """
