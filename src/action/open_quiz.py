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

        # load and check key/values
        try:
            answers = json.loads(content)
            assert 'quiz-version' in answers.keys(), 'No key "quiz-version" found.'
            for key, value in answers.items():
                assert isinstance(key, str), 'Expected str keys. Got {}'.format(type(value))
                assert isinstance(value, str), 'Expected str values. Got {}'.format(type(value))
        except Exception as err:
            raise BadRequest('Invalid file. {}'.format(str(err)))

        # compare versions
        if answers['quiz-version'] != self._quiz['version']:
            raise BadRequest('Version mismatch. Quiz runs v{} but answers are v{}. Do convert answers beforehand.'.format(
                self._quiz['version'], answers['quiz-version']
            ))

        self._data['answers'] = answers
        return render_template('quiz.html', **self._data), 200
