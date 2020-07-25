from flask import render_template
from flask.views import MethodView


class GetIndexAction(MethodView):
    def __init__(self, logger, title):
        super().__init__()
        self.__logger = logger
        self.__title = title

    def get(self):
        return render_template('home.html', title=self.__title), 200
