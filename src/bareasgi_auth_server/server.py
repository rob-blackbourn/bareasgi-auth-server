"""
Server
"""

import argparse
import asyncio
import logging
import logging.config

import pkg_resources
import uvicorn
import yaml
from bareasgi import Application
from bareasgi_auth_common.utils.yaml_types import initialise_types
from easydict import EasyDict
from hypercorn.asyncio import serve
from hypercorn.config import Config

from .app import make_application
from .utils import expand_path

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)

def load_config(filename: str) -> EasyDict:
    """Load the configuration"""
    initialise_types()
    with open(filename, 'rt') as file_ptr:
        return EasyDict(yaml.load(file_ptr, Loader=yaml.FullLoader))

def parse_args(argv: list):
    """Parse the command line args"""
    parser = argparse.ArgumentParser(
        description='Order File Service',
        add_help=False)

    parser.add_argument(
        '--help', help='Show usage',
        action='help')
    parser.add_argument(
        '-f', '--config-file', help='Path to the configuration file.',
        default=pkg_resources.resource_filename(__name__, "config.yml"),
        action="store", dest='CONFIG_FILE')

    return parser.parse_args(argv)
    
    
def initialise_logging(config: EasyDict) -> None:
    """Initialise the logging"""
    if 'logging' in config:
        logging.config.dictConfig(config.logging)


def start_uvicorn_server(app: Application, config: EasyDict) -> None:
    """Start the uvicorn ASGI server"""

    kwargs = {
        'host': config.host,
        'port': config.port,
        'log_level': 'debug'
    }

    if config.ssl.enabled:
        kwargs['ssl_keyfile'] = expand_path(config.ssl.keyfile)
        kwargs['ssl_certfile'] = expand_path(config.ssl.certfile)

    uvicorn.run(app, **kwargs)


def start_hypercorn_server(app: Application, config: EasyDict) -> None:
    """Start the hypercorn ASGI server"""

    web_config = Config()
    web_config.bind = [f'{config.host}:{config.port}']

    if config.ssl.enabled:
        web_config.keyfile = expand_path(config.ssl.keyfile)
        web_config.certfile = expand_path(config.ssl.certfile)

    asyncio.run(serve(app, web_config))


def start_http_server(app: Application, config: EasyDict) -> None:
    if config.http_server == "uvicorn":
        start_uvicorn_server(app, config)
    elif config.http_server == "hypercorn":
        start_hypercorn_server(app, config)
    else:
        logger.error('Unknown http server "%s"', config.http_server)
        raise Exception(f'Unknown http server "{config.http_server}"')


def start_server(argv):
    args = parse_args(argv[1:])
    config = load_config(args.CONFIG_FILE)
    initialise_logging(config)
    app = make_application(config)
    start_http_server(app, config.app)
    logging.shutdown()
