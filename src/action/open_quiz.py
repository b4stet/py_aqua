import json
from flask import request, render_template
from werkzeug.exceptions import BadRequest

from src.action.base import BaseAction


class OpenQuizAction(BaseAction):
    def __init__(self, logger, title, quiz):
        super().__init__(logger)
        self.__title = title
        self.__quiz = quiz

    def get(self):
        return render_template('upload.html', title=self.__title), 200

    def post(self):
        f = request.files['answers']
        content = f.read()

        # load and check key/values
        try:
            answers = json.loads(content)
            assert 'quiz-version' in answers.keys(), 'No key "quiz-version" found.'
            for value in answers:
                assert isinstance(value, str), 'Expected str values. Got {}'.format(type(value))
        except Exception as err:
            raise BadRequest('Invalid file. {}'.format(str(err)))

        # compare versions
        if answers['quiz-version'] != self.__quiz['version']:
            raise BadRequest('Version mismatch. Quiz runs v{} but answers are v{}. Do convert answers beforehand.'.format(
                self.__quiz['version'], answers['quiz-version']
            ))

        # prefill quiz
        return render_template('quiz.html', title=self.__title, quiz=self.__quiz, answers=answers), 200
