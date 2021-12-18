"""Example API server"""

import asyncio
from datetime import timedelta
import logging
import logging.config
from typing import Any, List, TypedDict

from graphql import (
    GraphQLSchema,
    GraphQLObjectType,
    GraphQLField,
    GraphQLNonNull,
    GraphQLString,
    GraphQLResolveInfo,
    GraphQLList
)
from hypercorn.asyncio import serve
from hypercorn.config import Config

from bareasgi import Application, HttpRequest, HttpResponse, text_writer
from bareasgi_cors import add_cors_middleware
from bareasgi_graphql_next import add_graphql_next
from bareutils import response_code

from bareasgi_auth_common import add_jwt_auth_middleware

LOGGER = logging.getLogger('example')


class Person(TypedDict):
    firstName: str
    lastName: str


PEOPLE: List[Person] = [
    {
        'firstName': 'rob',
        'lastName': 'blackbourn'
    },
    {
        'firstName': 'ann-marie',
        'lastName': 'dutton'
    }
]


async def people_resolver(_obj: Any, _info: GraphQLResolveInfo) -> List[Person]:
    return PEOPLE

PersonType = GraphQLObjectType(
    'Person',
    fields=lambda: {
        'firstName': GraphQLField(GraphQLNonNull(GraphQLString)),
        'lastName': GraphQLField(GraphQLNonNull(GraphQLString)),
    }
)

PeopleQuery = GraphQLField(
    GraphQLNonNull(GraphQLList(GraphQLNonNull(PersonType))),
    resolve=people_resolver
)

QueriesType = GraphQLObjectType(
    'Queries',
    fields=lambda: {
        "people": PeopleQuery
    }
)

SCHEMA = GraphQLSchema(
    query=QueriesType
)


async def hello(_request: HttpRequest) -> HttpResponse:
    LOGGER.debug('Handling hello request')

    return HttpResponse(
        response_code.OK,
        [(b'content-type', b'text/plain')],
        text_writer("Hello, World!")
    )


async def main_async():
    LOGGER.debug('Starting server')

    app = Application()

    add_cors_middleware(app)

    lease_expiry = timedelta(minutes=1)
    session_expiry = timedelta(minutes=2)

    add_jwt_auth_middleware(
        app,
        "A secret of less than 15 characters",
        lease_expiry,
        "jetblack.net",
        'bareasgi-auth',
        'jetblack.net',
        '/',
        session_expiry,
        '/auth/api/renew_token',
        '/auth/ui/login',
        []
    )

    app.http_router.add({'GET'}, '/example/api/hello', hello)

    add_graphql_next(app, SCHEMA, path_prefix='/example/api')

    config = Config()
    config.bind = ["0.0.0.0:10010"]
    # config.verify_mode = ssl.VerifyMode.CERT_NONE

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
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False
            },
            'bareasgi_auth_common': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False
            }
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['console']
        }
    })

    asyncio.run(main_async())
