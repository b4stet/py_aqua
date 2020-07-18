from flask import render_template
from flask.views import MethodView


class FillQuizAction(MethodView):
    def __init__(self, logger, title, quiz):
        super().__init__()
        self.__logger = logger
        self.__title = title
        self.__quiz = quiz

    def get(self):
        return render_template('quiz.html', title=self.__title), 200
