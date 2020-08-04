import copy
from flask.views import MethodView


class BaseAction(MethodView):
    MESSAGE_SUCCESS = 'success'
    MESSAGE_ERROR = 'danger'

    MODE_USER = 'user'
    MODE_REVIEWER = 'reviewer'

    def __init__(self, logger):
        self._logger = logger
