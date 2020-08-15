from flask import current_app, render_template
from werkzeug.exceptions import default_exceptions
import sys
import traceback

from src.action.base import BaseAction


class ErrorHandlerService():
    def __init__(self):
        self.__logger = current_app.logger
        self.__title = current_app.title
        self.__mode = current_app.config['mode']

    def init_app(self, app):
        app.register_error_handler(Exception, self.handler)
        for code, _ in default_exceptions.items():
            app.register_error_handler(code, self.handler)

    def handler(self, error):
        status_code = 500
        if hasattr(error, 'code'):
            status_code = error.code

        # format log line
        stack = traceback.format_tb(sys.exc_info()[2])
        error_location = stack[-1].split('\n')[0].strip(' ')
        error_type = type(error).__name__
        error_value = str(error).split('\n')[0]
        error_log = '[{}] {}: {}'.format(error_location, error_type, error_value)
        self.__logger.error(error_log, exc_info=True)

        # logger: full stack trace
        # 4xx as warning
        # 5xx as error
        if 500 <= status_code < 600:
            self.__logger.error(error_log, exc_info=True)
        else:
            self.__logger.warning(error_log, exc_info=True)

        # message to return
        detail = str(error)
        if 500 <= status_code < 600:
            detail = 'Server Error'

        message = {
            'type': BaseAction.MESSAGE_ERROR,
            'content': [
                'Error {}: {}'.format(status_code, error_type),
                detail,
            ],
        }

        data = {
            'title': self.__title,
            'message': message,
        }
        if self.__mode == BaseAction.MODE_REVIEWER:
            data['review'] = True

        return render_template('layout.html', **data), status_code
