from flask import g, current_app
import os

from src.action.get_index import GetIndexAction
from src.action.new_quiz import NewQuizAction
from src.action.open_quiz import OpenQuizAction
from src.action.save_quiz import SaveQuizAction


class DependenciesService():
    def __init__(self):
        self.__logger = current_app.logger
        self.__title = current_app.title
        self.__quiz = current_app.quiz
        self.__mode = current_app.config['mode']

    def init_app(self, app):
        self.register()

    def register(self):
        if 'di_container' not in g:
            g.di_container = {
                GetIndexAction: GetIndexAction.as_view('get_index', self.__logger, self.__title, self.__quiz),
                NewQuizAction: NewQuizAction.as_view('new_quiz', self.__logger, self.__title, self.__quiz),
                OpenQuizAction: OpenQuizAction.as_view('open_quiz', self.__logger, self.__mode, self.__title, self.__quiz),
                SaveQuizAction: SaveQuizAction.as_view('save_quiz', self.__logger, self.__mode),
            }

        return g.di_container
