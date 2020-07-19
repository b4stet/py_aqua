from flask.views import MethodView


class BaseAction(MethodView):
    def __init__(self, logger, title, quiz):
        self._logger = logger
        self._title = title
        self._quiz = quiz

    def validate_quiz(self):
        # verify section identifiers unicity
        self.__verify_unicity(self._quiz['sections'], 'section')

        tree_nodes = []
        for section in self._quiz['sections']:
            # verify group identifiers unicity per section
            tree_nodes.append('section {}'.format(section['id']))
            self.__verify_unicity(section['groups'], 'group', tree_nodes)

            for group in section['groups']:
                # verify item identifiers unicity per group
                tree_nodes.append('group {}'.format(group['id']))
                self.__verify_unicity(group['items'], 'item', tree_nodes)

                for item in group['items']:
                    # verify column identifiers unicity in table
                    if item['type'] == 'table':
                        tree_nodes.append('item {}'.format(item['id']))
                        self.__verify_unicity(item['columns'], 'column', tree_nodes)
                        tree_nodes.pop()

                    # verify values unicity in qcm
                    if item['type'] == 'qcm':
                        tree_nodes.append('item {}'.format(item['id']))
                        elements = item['options']
                        for elt in elements:
                            elt['id'] = elt.pop('value')
                        print(elements)
                        self.__verify_unicity(elements, 'option', tree_nodes)
                        tree_nodes.pop()

                tree_nodes.pop()
            tree_nodes.pop()

    def __verify_unicity(self, elements: dict, element_type, tree_nodes=None):
        identifiers = [element['id'] for element in elements]
        duplicates = set(identifier for identifier in identifiers if identifiers.count(identifier) > 1)
        if len(duplicates) > 0:
            message = 'Expected unique {} identifiers. Got duplicates'.format(element_type)
            if tree_nodes is not None:
                message += ' in ({})'.format(', '.join(tree_nodes))
            message += ': {}'.format(', '.join(duplicates))

            raise ValueError(message)
