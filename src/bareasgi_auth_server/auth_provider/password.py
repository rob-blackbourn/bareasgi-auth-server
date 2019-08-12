"""
Password
"""

from __future__ import annotations
from dataclasses import dataclass
import hashlib
import uuid

@dataclass
class Password:
    """Password"""

    id: int
    name: str
    salt: str
    hash: str
    state: str

    @classmethod
    def create(cls, name: str, password: str, state: str) -> Password:
        """Create a new password

        :param name: The name
        :type name: str
        :param password: The password in clear text
        :type password: str
        :param state: The password state
        :type state: str
        :return: True if the password was created, otherwise false
        :rtype: Password
        """
        salt = uuid.uuid4().hex
        hash_ = hashlib.sha512((password + salt).encode()).hexdigest()
        return Password(-1, name, salt, hash_, state)

    def is_valid_password(self, password: str) -> bool:
        """Check a password

        :param password: The password in clear text
        :type password: str
        :return: True if the password matches, otherwise false
        :rtype: bool
        """
        hash_ = hashlib.sha512((password + self.salt).encode()).hexdigest()
        return self.hash == hash_