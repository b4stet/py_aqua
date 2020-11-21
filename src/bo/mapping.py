from src.bo.base import BaseBO


class MappingBo(BaseBO):
    def __init__(self, logger, quiz, analysis):
        super().__init__(logger)
        self.__quiz = quiz
        self.__analysis = analysis

    def map_by_key(self, data, key):
        mapping = {}

        for elt in self.__analysis[data]:
            mapping[elt[key]] = {k: v for k, v in elt.items() if k != key}

        return mapping

    def map_items_by_full_id(self):
        item_mapping = {}
        for section in self.__quiz['sections']:
            sid = section['id']
            for group in section['groups']:
                gid = group['id']
                for item in group['items']:
                    full_id = '-'.join([sid, gid, item['id']])
                    item_mapping[full_id] = item
        return item_mapping

    def check_item_ids_unicity(self):
        ids = []
        for section in self.__quiz['sections']:
            sid = section['id']
            for group in section['groups']:
                gid = group['id']
                for item in group['items']:
                    identifier = '{}-{}-{}'.format(sid, gid, item['id'])
                    if item['type'] == self.ITEM_TABLE_SIMPLE:
                        for col in item['columns']:
                            ids.append('{}-{}'.format(identifier, col['id']))
                    elif item['type'] == self.ITEM_TABLE_DOUBLE:
                        for col in item['columns'][1:]:
                            ids.append('{}-{}'.format(identifier, col['id']))
                    else:
                        ids.append(identifier)
        duplicates = list(set('{} ({}x)'.format(i, ids.count(i)) for i in ids if ids.count(i) > 1))
        return duplicates
