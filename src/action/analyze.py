import json
from flask import request, render_template
from werkzeug.exceptions import BadRequest

from src.action.base import BaseAction
from src.lib import validate_json


class AnalyzeAction(BaseAction):
    def __init__(self, logger, mapping_bo, analysis_bo, answers_bo, mode, title, quiz):
        super().__init__(logger, mode, title, quiz)
        self.__mapping_bo = mapping_bo
        self.__analysis_bo = analysis_bo
        self.__answers_bo = answers_bo

    def get(self):
        self._data.update({
            'action': '/analysis/open',
            'placeholder': 'Choose review to load'
        })
        return render_template('upload.html', **self._data), 200

    def post(self):
        f = request.files['file']
        content = f.read()
        content_json = json.loads(content)

        # validate input
        try:
            validate_json.validate(content_json, self._title['short'], self._quiz['version'])
            answers, review, texts_gap, texts_remediation = self.__analysis_bo.extract_review(content_json)
        except ValueError as err:
            raise BadRequest('Cannot perform gap analysis. {}'.format(str(err)))

        # analyze
        mapping = {
            'sections_id_name': {section['id']: section['name'] for section in self._quiz['sections']},
            'items_by_full_id': self.__mapping_bo.map_items_by_full_id(),
            'scoring_by_grade': self.__mapping_bo.map_by_key('scoring', 'grade'),
            'statuses_by_label': self.__mapping_bo.map_by_key('statuses', 'label'),
            'priorities_by_label': self.__mapping_bo.map_by_key('priorities', 'label'),
            'categories_by_id': self.__mapping_bo.map_by_key('categories', 'id'),
        }

        analysis_sections, analysis_categories = self.__analysis_bo.analyze(review, texts_gap, texts_remediation, mapping)
        summary = self.__analysis_bo.summarize(analysis_sections, analysis_categories, mapping)
        appendix = self.__answers_bo.assemble(answers)

        # data to render
        self._data.update({
            'analysis': self.__analysis_bo.get_analysis_config(),
            'report_summary': summary,
            'report_categories': analysis_categories,
            'report_appendix': appendix,
        })

        return render_template('report.html', **self._data), 200
