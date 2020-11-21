class BaseBO():
    ITEM_QCM_UNIQUE = 'qcm_unique'
    ITEM_QCM_MULTIPLE = 'qcm_multiple'
    ITEM_TABLE_SIMPLE = 'table_simple'
    ITEM_TABLE_DOUBLE = 'table_double'
    ITEM_FREE_TEXT = 'text'

    REVIEW_DISABLED = 'disabled'

    def __init__(self, logger):
        self._logger = logger
