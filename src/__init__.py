import os
import yaml
from flask import Flask, Blueprint, g

from src.include.services import services
from src.include.routing import routing


def bootstrap(quiz_file):
    app_root = os.path.dirname(os.path.dirname(__file__))
    app = Flask(
        __name__,
        instance_path=app_root,
    )

    # set config
    quiz_config = config_from_yaml(quiz_file)
    app.title = quiz_config['title']
    app.quiz = quiz_config['quiz']

    # register components and return app
    with app.app_context():
        register_services(app)
        register_routes(app, g.di_container)
        return app


def config_from_yaml(quiz_file):
    with open(quiz_file, mode='r') as f:
        config = yaml.safe_load(f)
    return config


def register_services(app):
    for service in services:
        service().init_app(app)


def register_routes(app, di_container):
    for bp_name, actions in routing.items():
        blueprint = Blueprint(name=bp_name, import_name=__name__)

        for route in actions['routes']:
            blueprint.add_url_rule(route['uri'], view_func=di_container[route['action']], methods=route['methods'])

        app.register_blueprint(blueprint)
