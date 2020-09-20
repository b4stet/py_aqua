import json
from flask import request, render_template
from werkzeug.exceptions import BadRequest

from src.action.base import BaseAction
from src.lib import plot


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
        content_json = json.loads(content)
        answers = {k: v for k, v in content_json.items() if not k.endswith('-review')}
        review = {k: v for k, v in content_json.items() if k.endswith('-review')}
        if len(review) == 0:
            raise BadRequest('Cannot perform gap analysis. Uploaded file does not contain review keys.')

        missing_review = {k: v for k, v in review.items() if v == 'not_reviewed'}
        if len(missing_review) > 0:
            items = [k.strip('-review') for k in missing_review.keys()]
            raise BadRequest('Cannot perform gap analysis. Items not reviewed: {}'.format(', '.join(items)))

        scoring_map_by_grade = self.__get_map(self.__analysis['scoring'], 'grade')
        analysis_sections, analysis_categories = self.__get_analysis_from_review(review, scoring_map_by_grade)

        self._data.update({
            'analysis': self.__analysis,
            'report_sections': analysis_sections,
            'report_categories': analysis_categories,
            'report_summary': self.__get_summary_from_analysis(analysis_sections, analysis_categories, scoring_map_by_grade),
            'answers_summary': self.__get_answers_summary(answers),
        })

        return render_template('report.html', **self._data), 200

    def __get_answers_summary(self, answers):
        answers_summary = {}
        for section in self._quiz['sections']:
            sid = section['id']
            answers_summary[sid] = {
                'name': section['name'],
                'groups': {}
            }

            for group in section['groups']:
                gid = group['id']
                answers_summary[sid]['groups'][gid] = {
                    'name': group['name'],
                    'description': group['description'],
                    'answers': [],
                    'notes': answers['{}-{}-notes'.format(sid, gid)]
                }

                for item in group['items']:
                    iid = item['id']
                    full_id = '-'.join([sid, gid, iid])
                    answer = [v for k, v in answers.items() if k.startswith(full_id) and not k.endswith('-notes')]

                    # re-format as list of lines:  'col1 title: col1 answer / col2 title: col2 answer / ...'
                    if item['type'] == 'table_simple':
                        answer_grouped = []
                        nb_columns = len(item['columns'])
                        nb_rows = len(answer) // nb_columns
                        for i in range(0, nb_rows):
                            row = ['{}: {}'.format(item['columns'][j]['title'], answer[nb_rows*i + j]) for j in range(0, nb_columns)]
                            answer_grouped.append(' / '.join(row))
                        answer = answer_grouped

                    # re-format as list of lines
                    if item['type'] == 'table_double':
                        answer_grouped = []
                        nb_rows = len(item['rows'])
                        nb_columns = len(item['columns'])
                        for i in range(0, nb_rows):
                            row = ['{}: {}'.format(item['columns'][0]['title'], item['rows'][i])]
                            row += ['{}: {}'.format(item['columns'][j]['title'], answer[nb_rows*i + j]) for j in range(1, nb_columns)]
                            answer_grouped.append(' / '.join(row))
                        answer = answer_grouped

                    answers_summary[sid]['groups'][gid]['answers'].append({
                        'item': item['question'],
                        'answer': answer,
                    })
        return answers_summary

    def __get_analysis_from_review(self, review, scoring_map_by_grade):
        # init structures
        priorities_map_by_label = self.__get_map(self.__analysis['priorities'], 'label')
        categories_map_by_id = self.__get_map(self.__analysis['categories'], 'id')

        analysis_sections = {}
        score_max_sections = {}
        for section in self._quiz['sections']:
            analysis_sections[section['id']] = {
                'name': section['name'],
                'score': 0.0,
                'grade': None,
            }
            score_max_sections[section['id']] = 0.0

        analysis_categories = {}
        score_max_categories = {}
        for category in self.__analysis['categories']:
            weight = priorities_map_by_label[category['priority']]['weight']
            statuses = self.__get_map(self.__analysis['statuses'], 'label')
            for key, value in statuses.items():
                value['name'] = key.capitalize().replace('_', ' ')
                value['count'] = 0
            analysis_categories[category['id']] = {
                'name': category['name'],
                'score': 0.0,
                'grade': None,
                'tag': None,
                'weight': weight,
                'statuses': statuses,
                'gap_analysis': {section['id']: [] for section in self._quiz['sections']},
                'remediations': {section['id']: [] for section in self._quiz['sections']},
            }
            score_max_categories[category['id']] = 0.0

        # fill
        for review_id, value in review.items():
            item = self.__get_item_from_review_id(review_id)
            sid = review_id.split('-')[0]
            cid = item['analysis']['category']

            item_priority = item['analysis']['priority']
            item_weight = priorities_map_by_label[item_priority]['weight']
            review_elt = next(elt for elt in item['reviewer'] if elt['option'] == value)

            if value != self.REVIEW_DISABLED:
                score_max_sections[sid] += item_weight * max([elt['score'] for elt in item['reviewer']])
                analysis_sections[sid]['score'] += item_weight * review_elt['score']

                score_max_categories[cid] += item_weight * max([elt['score'] for elt in item['reviewer']])
                analysis_categories[cid]['score'] += item_weight * review_elt['score']
                analysis_categories[cid]['statuses'][review_elt['status']]['count'] += 1

            analysis_categories[cid]['gap_analysis'][sid].append(review_elt['review'])
            if review_elt['remediation'] is not None:
                analysis_categories[cid]['remediations'][sid].append({
                    'priority': item_priority,
                    'weight': item_weight,
                    'remediation': review_elt['remediation'],
                })

        # transform (score as percentage, deduce grade/tag, sort remediation, build plots)
        for sid, value in analysis_sections.items():
            percentage = value['score']/score_max_sections[sid] * 100.0
            if percentage < 0.0:
                percentage = 0.00
            value['score'] = round(percentage, 2)
            value['grade'] = self.__get_grade_from_score(value['score'])

        for cid, value in analysis_categories.items():
            percentage = value['score']/score_max_categories[cid] * 100.0
            if percentage < 0.0:
                percentage = 0.00
            value['score'] = round(percentage, 2)
            value['grade'] = self.__get_grade_from_score(value['score'])
            tag = scoring_map_by_grade[value['grade']]['tag']
            value['tag'] = categories_map_by_id[cid]['summary'][tag]
            value['remediations'] = {k: sorted(v, key=lambda x: x['weight'], reverse=True) for k, v in value['remediations'].items()}

            donut_title = 'Grade: {}'.format(value['grade'])
            analysis_categories[cid]['donut_single'] = plot.get_donut(value, donut_title, scoring_map_by_grade)
            analysis_categories[cid]['waffle_items'] = plot.get_waffle(value['statuses'], 'Answers to items by status')

        return analysis_sections, analysis_categories

    def __get_summary_from_analysis(self, analysis_sections, analysis_categories, scoring_map_by_grade):
        summary = {}

        # final score/grade/tag
        score = 0.0
        score_max = 0.0
        for category in analysis_categories.values():
            score += category['weight'] * category['score']
            score_max += category['weight'] * 100.0
        score = round(score/score_max * 100.0, 2)
        grade = self.__get_grade_from_score(score)
        tag = scoring_map_by_grade[grade]['tag']

        donut_data = {
            'score': score,
            'grade': grade,
        }
        donut_title = 'Final Grade: {}'.format(grade)

        # global status counts
        statuses = self.__get_map(self.__analysis['statuses'], 'label')
        for key, value in statuses.items():
            counts = [elt['statuses'][key]['count'] for elt in analysis_categories.values()]
            value['name'] = key.capitalize().replace('_', ' ')
            value['count'] = sum(counts)

        # main remediations
        main_remediations = {}

        for cid, analysis in analysis_categories.items():
            main_remediations[cid] = {
                'name': analysis['name'],
                'remediations': {},
            }
            category_remediations = analysis['remediations']
            for sid, remediations in category_remediations.items():
                top_remediations = [remediation for remediation in remediations if remediation['priority'] in self.__analysis['summary']['priorities']]
                if len(top_remediations) > 0:
                    main_remediations[cid]['remediations'][sid] = top_remediations

        summary = {
            'grade': grade,
            'tag': self.__analysis['summary']['text'][tag],
            'main_remediations': main_remediations,
            'donut_single': plot.get_donut(donut_data, donut_title, scoring_map_by_grade),
            'donut_categories': plot.get_donuts_concentric(analysis_categories.values(), 'Grades achieved by categories', scoring_map_by_grade),
            'lollipop_sections': plot.get_lollipop(analysis_sections.values(), 'Grades achieved by section', scoring_map_by_grade),
            'waffle_items': plot.get_waffle(statuses, 'Item answers by status'),
        }
        return summary

    def __get_map(self, src, key):
        mapping = {}

        for elt in src:
            mapping[elt[key]] = {k: v for k, v in elt.items() if k != key}

        return mapping

    def __get_item_from_review_id(self, review_id):
        sid, gid, iid, _ = review_id.split('-')
        section = next((s for s in self._quiz['sections'] if s['id'] == sid))
        group = next((g for g in section['groups'] if g['id'] == gid))
        item = next((i for i in group['items'] if i['id'] == iid))

        return item

    def __get_grade_from_score(self, score):
        scoring_sorted = sorted(self.__analysis['scoring'], key=lambda k: k['max'], reverse=True)
        grade = next((scoring['grade'] for scoring in scoring_sorted if scoring['min'] <= score), None)
        return grade
