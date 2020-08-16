import json
from flask import request, render_template
from werkzeug.exceptions import BadRequest

from src.action.base import BaseAction


class AnalyzeAction(BaseAction):
    def __init__(self, logger, mode, title, quiz, analysis):
        super().__init__(logger, mode, title, quiz)
        self.__analysis = analysis

    def get(self):
        self._data.update({
            'action': '/analysis/open',
            'placeholder': 'Choose review to load'
        })
        return render_template('upload.html', **self._data), 200

    def post(self):
        f = request.files['file']
        content = f.read()

        self._data.update({
            'analysis': self.__analysis,
            'report': {
                'grades': {
                    'final': 'C',
                    'c1': 'B',
                    'c2': 'C',
                },
                'labels': {
                    'final': 'intermediate',
                    'c1': 'strong',
                    'c2': 'intermediate',
                },
            },
        })

        return render_template('report.html', **self._data), 200
