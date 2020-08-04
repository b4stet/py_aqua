import json
from flask import request, render_template
from werkzeug.exceptions import BadRequest

from src.action.base import BaseAction


class OpenQuizAction(BaseAction):
    def __init__(self, logger, mode, title, quiz):
        super().__init__(logger)
        self.__title = title
        self.__quiz = quiz
        self.__mode = mode

    def get(self):
        return render_template('upload.html', title=self.__title), 200

    def post(self):
        f = request.files['answers']
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
        if answers['quiz-version'] != self.__quiz['version']:
            raise BadRequest('Version mismatch. Quiz runs v{} but answers are v{}. Do convert answers beforehand.'.format(
                self.__quiz['version'], answers['quiz-version']
            ))

        # prepare rendering
        data = {
            'title': self.__title,
            'quiz': self.__quiz,
            'answers': answers,
        }

        if self.__mode == self.MODE_REVIEWER:
            data['review'] = True

        # prefill quiz
        return render_template('quiz.html', **data), 200
