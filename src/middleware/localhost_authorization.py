from werkzeug.exceptions import Forbidden
from src.action.base import BaseAction


class LocalhostAuthorizationMiddleware():
    def __init__(self, mode):
        self.__mode = mode

    def check(self):
        if self.__mode != BaseAction.MODE_REVIEWER:
            raise Forbidden('Not authorized.')
