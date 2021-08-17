"""
Sqlite Auth Repository
"""

from .auth_repository import AuthRepository
from .sqlite_authentication_repository import SqliteAuthenticationRepository
from .sqlite_authorization_repository import SqliteAuthorizationRepository

class SqliteAuthRepository(AuthRepository):
    """Sqlite auth repository"""

    def __init__(self, dsn: str):
        super().__init__(
            SqliteAuthenticationRepository(dsn),
            SqliteAuthorizationRepository(dsn)
        )
