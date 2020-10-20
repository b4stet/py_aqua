from flask.views import MethodView
from werkzeug.exceptions import BadRequest
import json


class BaseAction(MethodView):
    MESSAGE_SUCCESS = 'success'
    MESSAGE_ERROR = 'danger'

    MODE_USER = 'user'
    MODE_REVIEWER = 'reviewer'

    def __init__(self, logger, mode, title, quiz):
        self._logger = logger
        self._quiz = quiz
        self._title = title
        self._data = {
            'title': title,
            'quiz': quiz,
        }
        if mode == self.MODE_REVIEWER:
            self._data['review'] = True
