import aiopg.sa
import sqlalchemy as sa
from typing import Optional
from .types import AuthProvider, User

USERS_TABLE_NAME = 'users'


def define_users_table(metadata: sa.MetaData) -> sa.Table:
    return sa.Table(
        USERS_TABLE_NAME,
        metadata,
        sa.Column('id', sa.Integer, nullable=False, primary_key=True, autoincrement=True),
        sa.Column('email', sa.Text, nullable=False),
        sa.Column('salt', sa.Text, nullable=False),
        sa.Column('password', sa.Text, nullable=False),
        sa.Column('is_enabled', sa.Boolean, nullable=False),
        sa.UniqueConstraint('email'),
        schema='auth'
    )


def ensure_users_table_exists(engine: sa.engine.Engine) -> sa.Table:
    metadata = sa.MetaData()
    table = define_users_table(metadata)
    if not engine.dialect.has_schema(engine, table.schema):
        engine.execute(sa.schema.CreateSchema(table.schema))
    metadata.create_all(engine)
    return table


class PostgresAuthProvider(AuthProvider):

    def __init__(self, dsn) -> None:
        self.dsn = dsn
        self.users_table = ensure_users_table_exists(sa.create_engine(dsn))


    async def create(self, user: User) -> bool:
        try:
            async with aiopg.sa.create_engine(self.dsn) as engine:
                async with engine.acquire() as con:
                    stmt = self.users_table.insert().values(
                        email=user.username,
                        salt=user.salt,
                        password=user.password,
                        is_enabled=user.is_enabled
                    )
                    await con.execute(stmt)
                    return True
        except Exception as error:
            print(error)
            return False


    async def read(self, username: str) -> Optional[User]:
        async with aiopg.sa.create_engine(self.dsn) as engine:
            async with engine.acquire() as con:
                stmt = sa.select([
                    self.users_table.c.email,
                    self.users_table.c.salt,
                    self.users_table.c.password,
                    self.users_table.c.is_enabled
                ]).where(
                    self.users_table.c.email == username
                )
                cursor = await con.execute(stmt)
                row = await cursor.fetchone()
                return None if row is None else User(*row.as_tuple())


    async def update(self, user: User) -> None:
        async with aiopg.sa.create_engine(self.dsn) as engine:
            async with engine.acquire() as con:
                stmt = self.users_table.update().where(
                    self.users_table.c.email == user.username
                ).values(
                    salt=user.salt,
                    password=user.password,
                    is_enabled=user.is_enabled
                )
                await con.execute(stmt)


    async def delete(self, username: str) -> None:
        async with aiopg.sa.create_engine(self.dsn) as engine:
            async with engine.acquire() as con:
                stmt = self.users_table.delete().where(
                    self.users_table.c.email == username
                )
                await con.execute(stmt)
