from flask import render_template

from src.action.base import BaseAction


class NewQuizAction(BaseAction):
    def get(self):
        return render_template('quiz.html', **self._data), 200
