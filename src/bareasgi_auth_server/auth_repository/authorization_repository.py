"""Types for auth provider"""

from __future__ import annotations
from abc import ABCMeta, abstractmethod
from typing import AbstractSet


class AuthorizationRepository(metaclass=ABCMeta):
    """The base class for member repositories"""

    @abstractmethod
    async def add_role(self, name: str, description: Optional[str] = None) -> bool:
        """Add a role
        
        :param name: The name
        :type name: str
        :param description: The description, defaults to None
        :type description: Optional[str], optional
        :return: True if the role was created, otherwise False
        :rtype: bool
        """

    @abstractmethod
    async def delete_role(self, name: str) -> bool:
        """Delete a role
        
        :param name: The name
        :type name: str
        :return: True if the roles was deleted, otherwise false.
        :rtype: bool
        """

    async def has_role(self, user: str, role: str) -> bool:
        """Discover whether the user has a role
        
        :param user: The user name
        :type user: str
        :param role: The role name
        :type role: str
        :return: True if the user has the role, otherwise false
        :rtype: bool
        """

    @abstractmethod
    async def role_exists(self, role: str) -> bool:
        """Discover if a roles exists
        
        :param role: The role name
        :type role: str
        :return: True if the role exists, otherwise false.
        :rtype: bool
        """
        
    @abstractmethod
    async def initialise(self) -> None:
        """Initialise the member repository"""

    @abstractmethod
    async def grant(self, user: str, role: str) -> bool:
        """Grant a role to a user
        
        :param user: The user name
        :type user: str
        :param role: The role name
        :type role: str
        :return: True if the role could be granted, otherwise false
        :rtype: bool
        """
        ...

    @abstractmethod
    async def revoke(self, user: str, role: str) -> bool:
        """Revoke a role from a user
        
        :param user: The user name
        :type user: str
        :param role: The role name
        :type role: str
        :return: True if the role could be revoked, otherwise false
        :rtype: bool
        """
        ...
    
    @abstractmethod
    async def users(self, role: str) -> AbstractSet[str]:
        """Return the users that have been granted the role
        
        :param role: The role name
        :type role: str
        :return: A set of the users that have been granted the roles
        :rtype: AbstractSet[str]
        """
        ...

    @abstractmethod
    async def roles(self, user: str) -> AbstractSet[str]:
        """Return the groups that the user has been granted
        
        :param user: The user
        :type user: str
        :return: The set of roles granted to the user
        :rtype: AbstractSet[str]
        """
        ...

    @abstractmethod
    async def update(self, user: str, roles: AbstractSet[str]) -> bool:
        """Update the user to have the given roles
        
        :param user: The user name
        :type user: str
        :param roles: The roles
        :type roles: AbstractSet[str]
        :return: True if the roles could be updated, otherwise false
        :rtype: bool
        """
        ...
