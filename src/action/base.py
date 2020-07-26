import copy
from flask.views import MethodView


class BaseAction(MethodView):
    MESSAGE_SUCCESS = 'success'
    MESSAGE_ERROR = 'danger'

    def __init__(self, logger):
        self._logger = logger
