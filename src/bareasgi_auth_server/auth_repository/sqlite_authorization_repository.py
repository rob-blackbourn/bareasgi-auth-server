"""Types for auth provider"""

from typing import AbstractSet, Optional

import aiosqlite

from .authorization_repository import AuthorizationRepository

class SqliteAuthorizationRepository(AuthorizationRepository):
    """The Sqlite authorization repository"""

    def __init__(self, dsn) -> None:
        self._dsn = dsn

    async def add_role(self, name: str, description: Optional[str] = None) -> bool:
        async with aiosqlite.connect(self._dsn) as conn:
            await conn.execute(
                "INSERT INTO roles(name, description) VALUES(?, ?)",
                (name, description)
            )
            await conn.commit()
            return conn.total_changes > 0

    async def delete_role(self, name: str) -> bool:
        async with aiosqlite.connect(self._dsn) as conn:
            await conn.execute("DELETE FROM roles WHERE name = ?", (name, ))
            await conn.commit()
            return conn.total_changes > 0

    async def has_role(self, user: str, role: str) -> bool:
        async with aiosqlite.connect(self._dsn) as conn:
            async with await conn.execute("""
                SELECT members.id
                FROM members
                INNER JOIN passwords
                ON passwords.name = ?
                AND passwords.id = members.user_id
                INNER JOIN roles
                ON roles.name = ?
                AND roles.id = members.role_id
            """, (user, role)) as cursor:
                row = await cursor.fetchone()
                return row is not None

    async def role_exists(self, role: str) -> bool:
        async with aiosqlite.connect(self._dsn) as conn:
            async with conn.execute("SELECT id FROM roles WHERE name = ?", (role,)) as cursor:
                row = await cursor.fetchone()
                return row is not None

    async def grant(self, user: str, role: str) -> bool:
        async with aiosqlite.connect(self._dsn) as conn:
            await conn.execute("""
                INSERT INTO members (user_id, role_id)
                SELECT passwords.id, roles.id
                FROM passwords
                CROSS JOIN roles
                ON roles.name = ?
                WHERE passwords.name = ?
            """, (role, user))
            await conn.commit()
            return conn.total_changes > 0

    async def revoke(self, user: str, role: str) -> bool:
        async with aiosqlite.connect(self._dsn) as conn:
            await conn.execute("""
                DELETE FROM members
                WHERE EXISTS (
                    SELECT members.id
                    FROM members
                    INNER JOIN passwords
                    ON passwords.name = ?
                    AND passwords.id = members.user_id
                    INNER JOIN roles
                    ON roles.name = ?
                    AND roles.id = members.role_id
                )
            """, (user, role))
            await conn.commit()
            return conn.total_changes > 0

    async def users(self, role: str) -> AbstractSet[str]:
        async with aiosqlite.connect(self._dsn) as conn:
            async with  await conn.execute("""
                SELECT passwords.name
                FROM passwords
                INNER JOIN members
                ON members.user_id = passwords.id
                INNER JOIN roles
                ON roles.name = ?
                AND roles.id = members.role_id
            """, (role,)) as cursor:
                return {row['name'] async for row in cursor}

    async def roles(self, user: str) -> AbstractSet[str]:
        async with aiosqlite.connect(self._dsn) as conn:
            async with  await conn.execute("""
                SELECT roles.name
                FROM roles
                INNER JOIN members
                ON members.role_id = roles.id
                INNER JOIN passwords
                ON passwords.name = ?
                AND passwords.id = members.role_id
            """, (user,)) as cursor:
                return {row['name'] async for row in cursor}

    async def update(self, user: str, roles: AbstractSet[str]) -> bool:
        async with aiosqlite.connect(self._dsn) as conn:
            await conn.execute("""
                DELETE members
                WHERE EXISTS (
                    SELECT members.id from members
                    INNER JOIN passwords
                    ON passwords.id = members.user_id
                    AND passwords.name = ?)
            """, (user,))
            await conn.execute("""
                INSERT INTO members(user_id, roles_id)
                SELECT passwords.id, roles.id
                FROM passwords
                CROSS JOIN roles
                ON roles.name IN ?
                WHERE passwords.name = ?
            """, (roles, user))
            await conn.commit()
            return conn.total_changes > 0

    async def initialise(self) -> None:
        async with aiosqlite.connect(self._dsn) as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS roles
                (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NULL,
                    UNIQUE(name)
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS members
                (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    role_id INTEGER NOT NULL,
                    UNIQUE(user_id, role_id),
                    FOREIGN KEY (user_id) references passwords(id),
                    FOREIGN KEY (role_id) references roles(id)
                )
            """)
            for role in ('grant', 'read.any', 'write.any'):
                if not await self.role_exists(role):
                    await self.add_role(role)
            for role in ('grant', 'read.any', 'write.any'):
                if not await self.has_role('admin', role):
                    await self.grant('admin', role)