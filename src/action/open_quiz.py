import json
from flask import request, render_template
from werkzeug.exceptions import BadRequest

from src.action.base import BaseAction


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
        self._data['answers'] = self._validate_and_get_json(content)

        return render_template('quiz.html', **self._data), 200
