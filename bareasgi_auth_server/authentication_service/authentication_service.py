"""
Authentication Service
"""

from abc import ABCMeta, abstractmethod
from typing import Any, Mapping, Optional


class AuthenticationService(metaclass=ABCMeta):
    """A base class for authentication services"""

    @abstractmethod
    async def authenticate(self, **credentials) -> Optional[str]:
        """Authenticate the user.

        Returns:
            Optional[str]: The user identifier or None if not authenticated.
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
    async def authorizations(self, user_id: str) -> Mapping[str, Any]:
        """Return the authorizations for the user.

        Args:
            user_id (str): The used identifier.

        Returns:
            Mapping[str, Any]: The authorizations.
        """
