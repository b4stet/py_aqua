from flask import render_template
from werkzeug.exceptions import BadRequest

from src.action.base import BaseAction


class GetIndexAction(BaseAction):
    def __init__(self, logger, title, quiz):
        super().__init__(logger)
        self.__title = title
        self.__quiz = quiz

    def get(self):
        # validate quiz config
        try:
            self.__check_item_ids()
        except ValueError as err:
            raise BadRequest('Invalid quiz config. {}'.format(str(err)))

        message = {
            'type': self.MESSAGE_SUCCESS,
            'content': [
                'Quiz config loaded.',
                'Running version {}.'.format(self.__quiz['version'])
            ],
        }

        return render_template('layout.html', title=self.__title, message=message), 200

    def __check_item_ids(self):
        ids = []
        for section in self.__quiz['sections']:
            sid = section['id']
            for group in section['groups']:
                gid = group['id']
                for item in group['items']:
                    identifier = '{}-{}-{}'.format(sid, gid, item['id'])
                    if item['type'] == 'table':
                        for col in item['columns']:
                            ids.append('{}-{}'.format(identifier, col['id']))
                    else:
                        ids.append(identifier)
        duplicates = set('{} ({}x)'.format(i, ids.count(i)) for i in ids if ids.count(i) > 1)
        if len(duplicates) > 0:
            raise ValueError('Expected unique identifiers. Got duplicates: {}'.format(', '.join(duplicates)))
