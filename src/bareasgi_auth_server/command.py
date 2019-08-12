from easydict import EasyDict as edict
import logging.config
import pkg_resources
import yaml
import uvicorn
from .server import make_app


def load_config():
    # initialise_types()
    with open(pkg_resources.resource_filename(__name__, 'config.yml'), 'rt') as fp:
        return edict(yaml.load(fp, Loader=yaml.FullLoader))


def start_server():
    config = load_config()
    logging.config.dictConfig(config.logging)
    app = make_app(config)
    uvicorn.run(app, port=config.app.port)
