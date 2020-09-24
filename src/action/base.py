from flask.views import MethodView
from werkzeug.exceptions import BadRequest
import json


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
        self._title = title
        self._data = {
            'title': title,
            'quiz': quiz,
        }
        if mode == self.MODE_REVIEWER:
            self._data['review'] = True

    def _validate_and_get_json(self, file):
        # load and check key/values
        try:
            content = json.loads(file)
            assert 'quiz-version' in content.keys(), 'No key "quiz-version" found.'
            for key, value in content.items():
                assert isinstance(key, str), 'Expected str keys. Got {}'.format(type(value))
                assert isinstance(value, str), 'Expected str values. Got {}'.format(type(value))
        except Exception as err:
            raise BadRequest('Invalid file. {}'.format(str(err)))

        # compare config
        if content['quiz-name'] != self._title['short']:
            raise BadRequest('Quiz mismatch. Running "{}" config but file is for "{}".'.format(
                self._title['short'], content['quiz-name']
            ))

        # compare versions
        if content['quiz-version'] != self._quiz['version']:
            raise BadRequest('Version mismatch. Running v{} but file has v{}. Do convert file beforehand.'.format(
                self._quiz['version'], content['quiz-version']
            ))

        return content
