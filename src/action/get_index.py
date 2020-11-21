from flask import render_template
from werkzeug.exceptions import BadRequest

from src.action.base import BaseAction


class GetIndexAction(BaseAction):
    def __init__(self, logger, mapping_bo, mode, title, quiz):
        super().__init__(logger, mode, title, quiz)
        self.__mapping_bo = mapping_bo

    def get(self):
        # validate quiz config
        duplicates = self.__mapping_bo.check_item_ids_unicity()
        if len(duplicates) > 0:
            raise BadRequest('Invalid quiz config. Expected unique identifiers. Got duplicates: {}'.format(', '.join(duplicates)))

        message = {
            'type': self.MESSAGE_SUCCESS,
            'content': [
                'Quiz config loaded.',
                'Running version {}.'.format(self._quiz['version'])
            ],
        }

        # render
        self._data['message'] = message
        return render_template('layout.html', **self._data), 200
