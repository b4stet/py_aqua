from flask import request, render_template
from werkzeug.exceptions import BadRequest
import json

from src.action.base import BaseAction
from src.lib import validate_json


class OpenQuizAction(BaseAction):
    def get(self):
        self._data.update({
            'action': '/quiz/open',
            'placeholder': 'Choose answers to load',
        })
        return render_template('upload.html', **self._data), 200

    def post(self):
        f = request.files['file']
        content = f.read()
        content_json = json.loads(content)

        try:
            validate_json.validate(content_json, self._title['short'], self._quiz['version'])
        except ValueError as err:
            raise BadRequest('Cannot load answers. {}'.format(str(err)))

        self._data['answers'] = content_json
        return render_template('quiz.html', **self._data), 200
