"""Types for auth provider"""

from __future__ import annotations
from abc import ABCMeta, abstractmethod
from typing import Optional

from .password import Password

class AuthenticationRepository(metaclass=ABCMeta):
    """The base class for authentication repositories"""

    @abstractmethod
    async def initialise(self) -> None:
        """Initialise the authentication repository"""

    @abstractmethod
    async def create(self, password: Password) -> Optional[Password]:
        """Create a password

        :param password: The password
        :type password: Password
        :return: True if the password was created, otherwise false.
        :rtype: bool
        """


    @abstractmethod
    async def read(self, name: str) -> Optional[Password]:
        """Read the password for the given name

        :param name: The name
        :type name: str
        :return: The password or None if not found
        :rtype: Optional[Password]
        """


    @abstractmethod
    async def update(self, password: Password) -> bool:
        """Update the password

        :param pasword: The password
        :type password: Password
        :return: True if the password was updated, otherwise false
        :rtype: bool
        """


    @abstractmethod
    async def delete(self, id_: int) -> bool:
        """Delete the password

        :param id_: The id
        :type id_: int
        :return: True if the password was deleted, otherwise false.
        :rtype: bool
        """
