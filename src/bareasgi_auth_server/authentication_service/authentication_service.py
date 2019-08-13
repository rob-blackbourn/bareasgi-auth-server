"""
Authentication Service
"""

from abc import ABCMeta, abstractmethod


class AuthenticationService(metaclass=ABCMeta):
    """A base class for authentication services"""

    @abstractmethod
    async def is_password_for_user(self, name: str, password: str) -> bool:
        """Return true if the password is valid for this user

        :param name: The user's name
        :type name: str
        :param password: The users password in clear text
        :type password: str
        :return: True if the password is correct, otherwise false
        :rtype: bool
        """


    @abstractmethod
    async def is_valid(self, name: str) -> bool:
        """Return true if the user's name is valid

        :param name: The user's name
        :type name: str
        :return: True if the name is valid, otherwise false.
        :rtype: bool
        """
