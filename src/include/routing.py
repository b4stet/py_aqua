from src.action.get_index import GetIndexAction
from src.action.fill_quiz import FillQuizAction

routing = {
    'quiz': {
        'routes': [
            {
                'uri': '/',
                'action': GetIndexAction,
                'methods': ['GET'],
            },
            {
                'uri': '/quiz/fill',
                'action': FillQuizAction,
                'methods': ['GET', 'POST'],
            },
            # {
            #     'uri': '/quiz/review',
            #     'action': 'ReviewQuizAction',
            #     'methods': ['GET', 'POST'],
            # },
        ],
    },

    # 'answers': {
    #     'routes': [
    #         {
    #             'uri': '/answers/import',
    #             'action': 'ImportAnswersAction',
    #             'methods': ['GET', 'POST'],
    #         },
    #         {
    #             'uri': '/answers/export',
    #             'action': 'ExportAnswersAction',
    #             'methods': ['GET'],
    #         },
    #     ]
    # },
}
