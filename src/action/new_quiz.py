from flask import render_template
from werkzeug.exceptions import BadRequest

from src.action.base import BaseAction


class NewQuizAction(BaseAction):
    def get(self):
        try:
            self.validate_quiz()
        except ValueError as err:
            raise BadRequest('Invalid quiz config. {}'.format(str(err)))

        return render_template('quiz.html', title=self._title, quiz=self._quiz), 200
