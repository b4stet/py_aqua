from flask import g, current_app
import logging
import sys
import time


class LoggerService():
    __HANDLERS = ['stdout', 'file', 'syslog']

    def __init__(self):
        self.__config = current_app.config['logger']

    def init_app(self, app):
        app.logger_name = self.__config['name']
        app.logger.setLevel('INFO')

        self.remove_default_handlers(app)
        for name, config in self.__config['handlers'].items():
            handler = self.configure_handler(name, config)
            if not isinstance(handler, logging.NullHandler):
                app.logger.addHandler(handler)

    # because 'default_handlers' property is only in flask >= 1.0 ...
    def remove_default_handlers(self, app):
        for i in range(0, len(app.logger.handlers))[::-1]:
            handler = app.logger.handlers[i]
            app.logger.removeHandler(handler)

    def configure_handler(self, name, config):
        handler = logging.NullHandler()
        if config['enabled'] is False or name not in self.__HANDLERS:
            return handler

        if name == 'stdout':
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(config['level'].upper())

        if name == 'file':
            handler = logging.FileHandler(
                filename=config['filename'],
                mode='a',
                encoding='utf-8',
                delay=False
            )
            handler.suffix = '%Y%m%d'
            handler.mode = 'a'
            handler.setLevel(config['level'].upper())

        if name == 'syslog':
            handler = logging.handlers.SysLogHandler(address=config['address'])
            handler.setLevel(config['level'].upper())
            handler.mapPriority(config['level'].upper())

        # set log format (time in UTC)
        formatter = logging.Formatter(
            fmt='%(asctime)s %(name)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S %Z'
        )
        formatter.converter = time.gmtime
        handler.setFormatter(formatter)

        return handler
