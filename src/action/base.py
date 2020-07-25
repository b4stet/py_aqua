import copy
from flask.views import MethodView


class BaseAction(MethodView):
    MESSAGE_SUCCESS = 'success'
    MESSAGE_ERROR = 'danger'

    def __init__(self, logger, title, quiz):
        self._logger = logger
        self._title = title
        self._quiz = quiz

    def validate_quiz(self):
        # verify section identifiers unicity
        self.__verify_unicity(self._quiz['sections'], 'id', 'section')

        tree_nodes = []
        for section in self._quiz['sections']:
            # verify group identifiers unicity per section
            tree_nodes.append('section {}'.format(section['id']))
            self.__verify_unicity(section['groups'], 'id', 'group', tree_nodes)

            for group in section['groups']:
                # verify item identifiers unicity per group
                tree_nodes.append('group {}'.format(group['id']))
                self.__verify_unicity(group['items'], 'id', 'item', tree_nodes)

                for item in group['items']:
                    # verify identifiers in table
                    if item['type'] == 'table':
                        # verify columns unicity
                        tree_nodes.append('item {}'.format(item['id']))
                        self.__verify_unicity(item['columns'], 'id', 'column', tree_nodes)

                        # verify values unicity in columns of type qcm
                        for col in item['columns']:
                            if col['type'] == 'qcm':
                                tree_nodes.append('column {}'.format(col['id']))
                                self.__verify_unicity(col['options'], 'value', 'option', tree_nodes)
                                tree_nodes.pop()

                        tree_nodes.pop()

                    # verify values unicity in qcm
                    if item['type'] == 'qcm':
                        tree_nodes.append('item {}'.format(item['id']))
                        self.__verify_unicity(item['options'], 'value', 'option', tree_nodes)
                        tree_nodes.pop()

                tree_nodes.pop()
            tree_nodes.pop()

    def __verify_unicity(self, elements: dict, key, element_type, tree_nodes=None):
        identifiers = [element[key] for element in elements]
        duplicates = set(identifier for identifier in identifiers if identifiers.count(identifier) > 1)
        if len(duplicates) > 0:
            message = 'Expected unique {} identifiers. Got duplicates'.format(element_type)
            if tree_nodes is not None:
                message += ' in ({})'.format(', '.join(tree_nodes))
            message += ': {}'.format(', '.join(duplicates))

            raise ValueError(message)
