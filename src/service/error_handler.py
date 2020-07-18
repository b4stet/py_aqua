from flask import current_app, render_template
from werkzeug.exceptions import default_exceptions
import sys
import traceback


class ErrorHandlerService():
    def __init__(self):
        self.__logger = current_app.logger
        self.__title = current_app.title

    def init_app(self, app):
        app.register_error_handler(Exception, self.handler)
        for code, _ in default_exceptions.items():
            app.register_error_handler(code, self.handler)

    def handler(self, error):
        status_code = 500
        if hasattr(error, 'code'):
            status_code = error.code

        # format of log line
        stack = traceback.format_tb(sys.exc_info()[2])
        error_location = stack[-1].split('\n')[0].strip(' ')
        error_type = type(error).__name__
        error_value = str(error).split('\n')[0]
        error_log = '[{}] {}: {}'.format(error_location, error_type, error_value)
        self.__logger.error(error_log, exc_info=True)

        err = {
            'message': str(error),
            'code': status_code,
        }
        return render_template('error.html', title=self.__title, error=err), status_code
