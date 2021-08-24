"""
Authentication Service
"""

from abc import ABCMeta, abstractmethod
from typing import AbstractSet, Optional


class AuthService(metaclass=ABCMeta):
    """A base class for authentication services"""

    @abstractmethod
    async def authenticate(self, **credentials) -> Optional[str]:
        """Authenticate the user.

        Returns:
            Optional[str]: The user identifier or None if not authenticated.
        """

    @abstractmethod
    async def is_valid_user(self, user: str) -> bool:
        """Check the user is still valid

        Args:
            user (str): The user identifier.

        Returns:
            bool: True if the user is valid otherwise false.
        """

    @abstractmethod
    async def authorizations(self, user: str) -> AbstractSet[str]:
        """Return the authorizations for the user.

        Args:
            user (str): The used identifier.

        Returns:
            Mapping[str, Any]: The authorizations.
        """
