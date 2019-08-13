"""
Application
"""

import os
import pkg_resources

from bareasgi import Application
from bareasgi_cors import CORSMiddleware
import bareasgi_jinja2
from easydict import EasyDict
import jinja2
from bareasgi_auth_common import JwtAuthenticator
from bareasgi_auth_common import TokenManager
from .authentication_controller import AuthenticationController
from .authentication_service import RepositoryAuthenticationService
from .authentication_repository import SqliteAuthenticationRepository


def make_application(config: EasyDict) -> Application:
    """Make the application

    :param config: The config
    :type config: EasyDict
    :return: The application
    :rtype: Application
    """
    templates_folder = pkg_resources.resource_filename(__name__, 'templates')

    cors_middleware = CORSMiddleware()

    app = Application(middlewares=[cors_middleware])

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(templates_folder),
        autoescape=jinja2.select_autoescape(['html', 'xml']),
        enable_async=True
    )

    bareasgi_jinja2.add_jinja2(app, env)

    domain = os.path.expandvars(config.token_manager.domain)
    issuer = os.path.expandvars(config.token_manager.issuer)
    secret = os.path.expandvars(config.token_manager.secret)
    path = config.token_manager.path
    token_expiry = config.token_manager.token_expiry
    cookie_name = config.token_manager.cookie_name
    max_age = config.token_manager.max_age

    authentication_service = RepositoryAuthenticationService(
        SqliteAuthenticationRepository(config.sqlite.url)
    )
    token_manager = TokenManager(
        secret,
        token_expiry,
        issuer,
        cookie_name,
        domain,
        path,
        max_age
    )

    token_renewal_path = config.app.path_prefix + config.token_manager.token_renewal_path
    authenticator = JwtAuthenticator(token_renewal_path, token_manager)

    auth_controller = AuthenticationController(
        config.app.path_prefix,
        config.app.login_expiry,
        token_manager,
        authentication_service,
        authenticator)

    auth_controller.add_routes(app)

    return app
