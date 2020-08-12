from src.action.get_index import GetIndexAction
from src.action.new_quiz import NewQuizAction
from src.action.open_quiz import OpenQuizAction
from src.action.save_quiz import SaveQuizAction
from src.action.analyze import AnalyzeAction

routing = {
    'quiz': {
        'routes': [
            {
                'uri': '/',
                'action': GetIndexAction,
                'methods': ['GET'],
            },
            {
                'uri': '/quiz/new',
                'action': NewQuizAction,
                'methods': ['GET'],
            },
            {
                'uri': '/quiz/open',
                'action': OpenQuizAction,
                'methods': ['GET', 'POST'],
            },
            {
                'uri': '/quiz/save',
                'action': SaveQuizAction,
                'methods': ['POST'],
            },
        ],
    },
    'analysis': {
        'routes': [
            {
                'uri': '/analysis/open',
                'action': AnalyzeAction,
                'methods': ['GET', 'POST'],
            },
        ]
    }
}
