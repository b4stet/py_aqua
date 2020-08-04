from flask import render_template

from src.action.base import BaseAction


class NewQuizAction(BaseAction):
    def __init__(self, logger, title, quiz):
        super().__init__(logger)
        self.__title = title
        self.__quiz = quiz

    def get(self):
        data = {
            'title': self.__title,
            'quiz': self.__quiz,
        }
        return render_template('quiz.html', **data), 200
