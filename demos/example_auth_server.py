"""Example Auth server"""

import asyncio
from datetime import timedelta
import logging
import logging.config
import socket
from typing import List, Any, Dict

from hypercorn.asyncio import serve
from hypercorn.config import Config
from bareasgi import Application
from bareasgi_auth_common import TokenManager
from bareasgi_auth_server import (
    AuthController,
    AuthService,
    UserNotFoundError,
    UserCredentialsError,
    UserInvalidError
)

LOGGER = logging.getLogger('example')


def getdomainname() -> str:
    hostname = socket.gethostname()
    fqdn = socket.getfqdn()
    return fqdn[len(hostname)+1:]


class MockAuthService(AuthService):

    def __init__(self) -> None:
        self.users: Dict[str, Any] = {
            'tom@example.com': {
                'password': 'foo',
                'is_valid': True,
                'authorizations': [
                    'read',
                    'write'
                ]
            },
            'dick@example.com': {
                'password': 'bar',
                'is_valid': True,
                'authorizations': [
                    'read',
                ]
            },
            'harry@example.com': {
                'password': 'grum',
                'is_valid': False,
                'authorizations': [
                    'read',
                    'write'
                ]
            }
        }

    async def authenticate(self, **credentials) -> str:
        user_id = credentials['username']
        user = self.users.get(user_id)

        if user is None:
            raise UserNotFoundError
        if user['password'] != credentials['password']:
            raise UserCredentialsError(user_id)
        if not user['is_valid']:
            raise UserInvalidError

        return user_id

    async def is_valid_user(self, user_id: str) -> bool:
        user = self.users.get(user_id)
        return user is not None and user['is_valid']

    async def authorizations(self, user_id: str) -> List[str]:
        user = self.users.get(user_id)
        if user is None:
            return []
        return user['authorizations']


async def main_async():
    LOGGER.debug('Starting server')
    app = Application()

    domain = getdomainname()
    issuer = domain
    lease_expiry = timedelta(minutes=1)
    session_expiry = timedelta(minutes=2)

    token_manager = TokenManager(
        "A secret of less than 15 characters",
        lease_expiry,
        issuer,
        'bareasgi-auth',
        domain,
        '/',
        session_expiry
    )
    auth_controller = AuthController(
        '/auth/api',
        token_manager,
        MockAuthService()
    )
    auth_controller.add_routes(app)

    config = Config()
    config.bind = ["0.0.0.0:10000"]

    await serve(app, config)  # type: ignore

if __name__ == '__main__':
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'simple': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'simple',
                'stream': 'ext://sys.stdout'
            }
        },
        'loggers': {
            'example': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False
            },
            'bareasgi': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': False
            },
            'bareasgi_auth_common': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False
            },
            'bareasgi_auth_server': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False
            },
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['console']
        }
    })

    asyncio.run(main_async())
