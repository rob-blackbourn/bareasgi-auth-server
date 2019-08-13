"""
LDAP Authentication Service
"""

from typing import AbstractSet, Any

import bonsai

from .authentication_service import AuthenticationService

class LdapAuthenticationService(AuthenticationService):
    """An LDAP authentication service"""

    def __init__(self, url: str, username: str, password: str, base: str) -> None:
        self.url = url
        self.username = username
        self.password = password
        self.base = base

    async def is_password_for_user(self, name: str, password: str) -> bool:
        try:
            client = bonsai.LDAPClient(self.url)
            client.set_credentials("SIMPLE", user=name, password=password)
            async with client.connect(is_async=True):
                return True
        except Exception:
            return False

    async def is_valid(self, name: str) -> bool:
        client = bonsai.LDAPClient(self.url)
        client.set_credentials("SIMPLE", user=self.username, password=self.password)
        async with client.connect(is_async=True) as connection:
            results = await connection.search(
                self.base,
                bonsai.LDAPSearchScope.SUBTREE,
                f'(&(userAccountControl:1.2.840.113556.1.4.803:=2)(userPrincipalName={name}))',
                ['userPrincipalName']
            )
            return len(results) == 0


    async def disabled_users(self) -> AbstractSet[str]:
        """Find all disabled users"""
        client = bonsai.LDAPClient(self.url)
        client.set_credentials("SIMPLE", user=self.username, password=self.password)
        async with client.connect(is_async=True) as connection:
            results = await connection.search(
                self.base,
                bonsai.LDAPSearchScope.SUBTREE,
                '(userAccountControl:1.2.840.113556.1.4.803:=2)',
                ['userPrincipalName']
            )
            users = {entry['userPrincipalName'][0] for entry in results}
            return users


    async def _ldap_groups(self, user_attr: str, user_value: Any) -> AbstractSet[str]:
        client = bonsai.LDAPClient(self.url)
        client.set_credentials("SIMPLE", user=self.username, password=self.password)
        async with client.connect(is_async=True) as connection:
            results = await connection.search(
                self.base,
                bonsai.LDAPSearchScope.SUBTREE,
                f'({user_attr}={user_value})',
                ['memberOf'])
            members = [entry['memberOf'] for entry in results if len(entry['memberOf']) > 0]
            groups = set()
            for items in members:
                for item in items:
                    _, cn = next(
                        filter(lambda x: x[0].lower() == 'cn', (i.split('=', maxsplit=1) for i in item.split(','))),
                        [None, None])
                    groups.add(cn)
            return groups


    async def ldap_groups_by_user_principal_name(self, user: str) -> AbstractSet[str]:
        """Get the groups for a user by user principal name"""
        return await self._ldap_groups('userPrincipalName', user)


    async def ldap_groups_by_sam_account_name(self, user: str) -> AbstractSet[str]:
        """Get the groups for a user by sam  principal name"""
        return await self._ldap_groups('sAMAccountName', user)
