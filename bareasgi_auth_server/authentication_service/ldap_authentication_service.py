"""
LDAP Authentication Service
"""

from typing import AbstractSet, Any, List, Mapping, Optional, Set

import bonsai

from .authentication_service import AuthenticationService


class LdapAuthenticationService(AuthenticationService):
    """An LDAP authentication service"""

    def __init__(
            self,
            url: str,
            username: Optional[str],
            password: Optional[str],
            base: Optional[str]
    ) -> None:
        """Initialise the LDAP authentication service.

        If a username and password are supplied, groups are returned with the
        credentials.

        Args:
            url (str): The LDAP user. e.g. ldaps://server1.example.com
            username (Optional[str]): An optional account with read access.
            password (Optional[str]): The password for the read-only account.
            base (Optional[str]): The base for the search string. e.g.
                ou=Users,ou=London,dc=example,dc=com
        """
        self.url = url
        self.username = username
        self.password = password
        self.base = base

    async def authorizations(self, user_id: str) -> Mapping[str, Any]:
        groups = await self.ldap_groups_by_sam_account_name(user_id)

        return {
            'roles': groups
        }

    async def authenticate(self, **credentials) -> Optional[str]:
        username = credentials['username']
        password = credentials['password']

        try:
            client = bonsai.LDAPClient(self.url)
            client.set_credentials(
                "SIMPLE",
                user=username,
                password=password
            )
            async with client.connect(is_async=True):
                if await self.is_valid_user(username):
                    return username

        except:  # pylint: disable=bare-except
            pass

        return None

    async def is_valid_user(self, user_id: str) -> bool:
        if self.username is None or self.password is None:
            return True

        client = bonsai.LDAPClient(self.url)
        client.set_credentials(
            "SIMPLE",
            user=self.username,
            password=self.password
        )
        async with client.connect(is_async=True) as connection:
            results = await connection.search(
                self.base,
                bonsai.LDAPSearchScope.SUBTREE,
                f'(&(userAccountControl:1.2.840.113556.1.4.803:=2)(userPrincipalName={user_id}))',
                ['userPrincipalName']
            )
            return len(results) == 0

    async def disabled_users(self) -> AbstractSet[str]:
        """Find all disabled users"""
        if self.username is None or self.password is None:
            return set()

        client = bonsai.LDAPClient(self.url)
        client.set_credentials(
            "SIMPLE", user=self.username, password=self.password)
        async with client.connect(is_async=True) as connection:
            results = await connection.search(
                self.base,
                bonsai.LDAPSearchScope.SUBTREE,
                '(userAccountControl:1.2.840.113556.1.4.803:=2)',
                ['userPrincipalName']
            )
            users = {entry['userPrincipalName'][0] for entry in results}
            return users

    async def _ldap_groups(self, user_attr: str, user_value: Any) -> List[str]:
        if self.username is None or self.password is None:
            return []

        client = bonsai.LDAPClient(self.url)
        client.set_credentials(
            "SIMPLE",
            user=self.username,
            password=self.password
        )
        async with client.connect(is_async=True) as connection:
            results = await connection.search(
                self.base,
                bonsai.LDAPSearchScope.SUBTREE,
                f'({user_attr}={user_value})',
                ['memberOf']
            )
            members: List[str] = [
                entry['memberOf']
                for entry in results if len(entry['memberOf']) > 0
            ]
            groups: Set[str] = set()
            for items in members:
                for item in items:
                    _, cn = next(
                        filter(
                            lambda x: x[0].lower() == 'cn',
                            (
                                i.split('=', maxsplit=1)
                                for i in item.split(',')
                            )
                        ),
                        [None, None]
                    )
                    if cn is not None:
                        groups.add(cn)
            return list(groups)

    async def ldap_groups_by_user_principal_name(self, user: str) -> List[str]:
        """Get the groups for a user by user principal name"""
        return await self._ldap_groups('userPrincipalName', user)

    async def ldap_groups_by_sam_account_name(self, user: str) -> List[str]:
        """Get the groups for a user by sam  principal name"""
        return await self._ldap_groups('sAMAccountName', user)
