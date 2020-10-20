class MappingBo():
    def __init__(self, logger, quiz, analysis):
        self._logger = logger
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
