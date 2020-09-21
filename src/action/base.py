from flask.views import MethodView


class BaseAction(MethodView):
    MESSAGE_SUCCESS = 'success'
    MESSAGE_ERROR = 'danger'

    MODE_USER = 'user'
    MODE_REVIEWER = 'reviewer'

    ITEM_QCM_UNIQUE = 'qcm'
    ITEM_QCM_MULTIPLE = 'list'
    ITEM_TABLE_SIMPLE = 'table_simple'
    ITEM_TABLE_DOUBLE = 'table_double'
    ITEM_FREE_TEXT = 'text'

    REVIEW_DISABLED = 'disabled'

    def __init__(self, logger, mode, title, quiz):
        self._logger = logger
        self._quiz = quiz
        self._data = {
            'title': title,
            'quiz': quiz,
        }
        if mode == self.MODE_REVIEWER:
            self._data['review'] = True
