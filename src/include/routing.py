from src.action.get_index import GetIndexAction
from src.action.new_quiz import NewQuizAction
from src.action.open_quiz import OpenQuizAction
from src.action.save_quiz import SaveQuizAction

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
}
