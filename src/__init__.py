import os
import yaml
from flask import Flask, Blueprint, g

from src.include.services import services
from src.include.routing import routing


def bootstrap(app_config, quiz_config, mode):
    app_root = os.path.dirname(os.path.dirname(__file__))
    app = Flask(
        __name__,
        instance_path=app_root,
    )

    # set config
    app_config = app_from_yaml(app_config, mode)
    app.config.update(app_config)
    app.debug = app.config['debug']

    config_quiz = quiz_from_yaml(quiz_config)
    app.title = config_quiz['title']
    app.quiz = config_quiz['quiz']

    # register components and return app
    with app.app_context():
        register_services(app)
        register_routes(app, g.di_container)
        return app


def quiz_from_yaml(quiz_config):
    yaml.add_constructor('!include', yaml_include_constructor, Loader=yaml.SafeLoader)
    with open(quiz_config, mode='r') as f:
        config = yaml.safe_load(f)
    return config


def app_from_yaml(app_config, mode):
    with open(app_config, mode='r') as f:
        config = yaml.safe_load(f)
    app_config = config.get(mode, config)
    app_config['mode'] = mode
    return app_config


def register_services(app):
    for service in services:
        service().init_app(app)


def register_routes(app, di_container):
    for bp_name, actions in routing.items():
        blueprint = Blueprint(name=bp_name, import_name=__name__)

        for route in actions['routes']:
            blueprint.add_url_rule(route['uri'], view_func=di_container[route['action']], methods=route['methods'])

        app.register_blueprint(blueprint)


def yaml_include_constructor(loader, node):
    root = os.path.dirname(os.path.dirname(__file__))
    filename = os.path.join(root, 'config', loader.construct_scalar(node))
    with open(filename, mode='r') as f:
        return yaml.safe_load(f)
