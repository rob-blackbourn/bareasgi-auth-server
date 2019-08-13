"""A Postgres Auth Provider"""

from typing import Optional

import aiosqlite

from .password import Password
from .authentication_repository import AuthenticationRepository


class SqliteAuthenticationRepository(AuthenticationRepository):
    """Sqlite Auth Provider"""

    def __init__(self, dsn) -> None:
        self._dsn = dsn


    async def create(self, password: Password) -> Optional[Password]:
        try:
            async with aiosqlite.connect(self._dsn) as conn:
                result = await conn.execute("""
                    INSERT INTO passwords(name, salt, hash, state)
                    VALUES (?, ?, ?, ?)
                """, (password.name, password.salt, password.hash, password.state))
                await conn.commit()
                result = await self.read(password.name)
                return result
        except aiosqlite.IntegrityError:
            return None


    async def read(self, name: str) -> Optional[Password]:
        async with aiosqlite.connect(self._dsn) as conn:
            cursor = await conn.execute("SELECT * from passwords where name = ?", (name, ))
            row = await cursor.fetchone()
            return None if row is None else Password(*row)


    async def update(self, password: Password) -> bool:
        async with aiosqlite.connect(self._dsn) as conn:
            await conn.execute(
                "UPDATE passwords SET name=?, salt=?, hash=?, state=? where id=?",
                (password.name, password.salt, password.hash, password.state, password.id)
            )
            await conn.commit()
            return conn.total_changes > 0

    async def delete(self, id_: int) -> bool:
        async with aiosqlite.connect(self._dsn) as conn:
            await conn.execute("DELETE FROM passwords WHERE id=?", (id_,))
            await conn.commit()
            return conn.total_changes > 0

    async def initialise(self) -> None:
        async with aiosqlite.connect(self._dsn) as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS passwords
                (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    hash TEXT NOT NULL,
                    state TEXT NOT NULL,
                    UNIQUE(name)
                )
            """)
        await self.create(Password.create("admin", "trustno1", "active"))
