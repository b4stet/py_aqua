from src.lib import plot


class GapAnalysisBo():
    REVIEW_DISABLED = 'disabled'

    def __init__(self, logger, analysis):
        self._logger = logger
        self.__analysis = analysis

    def get_analysis_config(self):
        return self.__analysis

    def extract_review(self, data):
        # extract answers and review
        answers = {k: v for k, v in data.items() if not k.endswith('-review')}
        review = {k: v for k, v in data.items() if k.endswith('-review')}

        # verify all items are reviewed
        if len(review) == 0:
            raise ValueError('Uploaded file does not contain review keys.')

        missing_review = {k: v for k, v in review.items() if v == 'not_reviewed'}
        if len(missing_review) > 0:
            items = [k for k in missing_review.keys()]
            raise ValueError('Items not reviewed: {}'.format(', '.join(items)))

        return answers, review

    def analyze(self, review, mapping):
        # sections analysis initialization (score, grade)
        analysis_sections = {}
        score_max_sections = {}
        for sid, name in mapping['sections_id_name'].items():
            analysis_sections[sid] = {
                'name': name,
                'score': 0.0,
                'grade': None,
            }
            score_max_sections[sid] = 0.0

        # categories analysis initialization (score, grade, status distribution, gap analysis per sections, remediations per sections)
        analysis_categories = {}
        score_max_categories = {}
        for category in self.__analysis['categories']:
            statuses = {}
            for label, config in mapping['statuses_by_label'].items():
                statuses[label] = {**config}
                statuses[label].update({
                    'name': label.capitalize().replace('_', ' '),
                    'count': 0,
                })

            analysis_categories[category['id']] = {
                'name': category['name'],
                'score': 0.0,
                'grade': None,
                'tag': None,
                'weight': mapping['priorities_by_label'][category['priority']]['weight'],
                'statuses': statuses,
                'gap_analysis': {sid: [] for sid in mapping['sections_id_name'].keys()},
                'remediations': {sid: [] for sid in mapping['sections_id_name'].keys()},
            }
            score_max_categories[category['id']] = 0.0

        # fill
        for review_id, value in review.items():
            # get item from id, and retrieve section/category id
            full_id = review_id[:-len('-review')]
            item = mapping['items_by_full_id'][full_id]
            sid = review_id.split('-')[0]
            cid = item['analysis']['category']

            item_priority = item['analysis']['priority']
            item_weight = mapping['priorities_by_label'][item_priority]['weight']

            # get config for the review
            review_elt = next(elt for elt in item['reviewer'] if elt['option'] == value)

            if value != self.REVIEW_DISABLED:
                # section score
                score_max_sections[sid] += item_weight * max([elt['score'] for elt in item['reviewer'] if elt['option'] != self.REVIEW_DISABLED])
                analysis_sections[sid]['score'] += item_weight * review_elt['score']

                # category score and status distribution
                score_max_categories[cid] += item_weight * max([elt['score'] for elt in item['reviewer'] if elt['option'] != self.REVIEW_DISABLED])
                analysis_categories[cid]['score'] += item_weight * review_elt['score']
                analysis_categories[cid]['statuses'][review_elt['status']]['count'] += 1

                # gap analysis
                analysis_categories[cid]['gap_analysis'][sid].append({
                    'section_name': mapping['sections_id_name'][sid],
                    'analysis': review_elt['review'],
                })

                # remediation
                if review_elt['remediation'] is not None:
                    # for list of top remediations in summary
                    is_top = False
                    if review_elt['score'] <= self.__analysis['summary']['score_min']:
                        is_top = True
                    analysis_categories[cid]['remediations'][sid].append({
                        'section_name': mapping['sections_id_name'][sid],
                        'priority': item_priority,
                        'weight': item_weight,
                        'remediation': review_elt['remediation'],
                        'is_top': is_top,
                    })

        # transform score as percentage, deduce grade for sections
        for sid, value in analysis_sections.items():
            percentage = value['score']/score_max_sections[sid] * 100.0
            if percentage < 0.0:
                percentage = 0.00
            value['score'] = round(percentage, 2)
            value['grade'] = self.convert_score2grade(value['score'])

        # transform score as percentage, deduce grade and tag, sort remediation, build plots for categories
        for cid, value in analysis_categories.items():
            # deduce percentage, grade
            percentage = value['score']/score_max_categories[cid] * 100.0
            if percentage < 0.0:
                percentage = 0.00
            value['score'] = round(percentage, 2)
            value['grade'] = self.convert_score2grade(value['score'])
            tag = mapping['scoring_by_grade'][value['grade']]['tag']
            value['tag'] = mapping['categories_by_id'][cid]['summary'][tag]

            # sort remediations
            value['remediations'] = {k: sorted(v, key=lambda x: x['weight'], reverse=True) for k, v in value['remediations'].items()}
            value['remediations'] = {k: sorted(v, key=lambda x: x['is_top'], reverse=True) for k, v in value['remediations'].items()}

            # grade and status distribution plots
            donut_title = 'Grade: {}'.format(value['grade'])
            analysis_categories[cid]['donut_result'] = plot.get_donut(value, donut_title, mapping['scoring_by_grade'])
            analysis_categories[cid]['waffle_items'] = plot.get_waffle(value['statuses'], 'Items distribution by status')

        return analysis_sections, analysis_categories

    def summarize(self, analysis_sections, analysis_categories, mapping):
        summary = {}

        # final score/grade/tag
        score = 0.0
        score_max = 0.0
        for category in analysis_categories.values():
            score += category['weight'] * category['score']
            score_max += category['weight'] * 100.0
        score = round(score/score_max * 100.0, 2)
        grade = self.convert_score2grade(score)
        tag = mapping['scoring_by_grade'][grade]['tag']

        # global status distribution
        statuses = {}
        for label, config in mapping['statuses_by_label'].items():
            counts = [elt['statuses'][label]['count'] for elt in analysis_categories.values()]
            statuses[label] = {**config}
            statuses[label].update({
                'name': label.capitalize().replace('_', ' '),
                'count': sum(counts),
            })

        # main remediations per categories
        main_remediations = {}
        for cid, analysis in analysis_categories.items():
            main_remediations[cid] = {
                'count': 0,
                'category_name': analysis['name'],
                'remediations': [],
            }
            category_remediations = analysis['remediations']

            # loop on remediations
            for sid, remediations in category_remediations.items():
                # 'top' defined by set of priority and flag
                top_remediations = []
                for remediation in remediations:
                    if remediation['priority'] in self.__analysis['summary']['priorities'] and remediation['is_top'] is True:
                        top_remediations.append(remediation)
                if len(top_remediations) > 0:
                    main_remediations[cid]['remediations'].append({
                        'section_name': analysis_sections[sid]['name'],
                        'remediations': top_remediations,
                    })
                    main_remediations[cid]['count'] += len(top_remediations)

        # grade, tag, remediations and plots (final grade, grade per categories, grade per sections, status distribution)
        donut_data = {
            'score': score,
            'grade': grade,
        }
        donut_title = 'Final Grade: {}'.format(grade)

        summary = {
            'grade': grade,
            'tag': self.__analysis['summary']['text'][tag],
            'main_remediations': main_remediations,
            'donut_result': plot.get_donut(donut_data, donut_title, mapping['scoring_by_grade']),
            'donut_categories': plot.get_donuts_concentric(analysis_categories.values(), 'Grades achieved by categories', mapping['scoring_by_grade']),
            'lollipop_sections': plot.get_lollipop(analysis_sections.values(), 'Grades achieved by section', mapping['scoring_by_grade']),
            'waffle_items': plot.get_waffle(statuses, 'Items distribution by status'),
        }

        return summary

    def convert_score2grade(self, score):
        scoring_sorted = sorted(self.__analysis['scoring'], key=lambda k: k['max'], reverse=True)
        grade = next((scoring['grade'] for scoring in scoring_sorted if scoring['min'] <= score), None)
        return grade
