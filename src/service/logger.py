from flask import g, current_app
import logging
import sys
import time


class LoggerService():
    def __init__(self):
        pass

    def init_app(self, app):
        app.logger_name = 'AQUA'
        app.logger.setLevel('INFO')

        self.remove_default_handlers(app)
        handler = self.configure_handler()

    # because 'default_handlers' property is only in flask >= 1.0 ...
    def remove_default_handlers(self, app):
        for i in range(0, len(app.logger.handlers))[::-1]:
            handler = app.logger.handlers[i]
            app.logger.removeHandler(handler)

    def configure_handler(self):
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel('INFO')

        # set log format (time in UTC)
        formatter = logging.Formatter(
            fmt='%(asctime)s %(name)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S %Z'
        )
        formatter.converter = time.gmtime
        handler.setFormatter(formatter)

        return handler
