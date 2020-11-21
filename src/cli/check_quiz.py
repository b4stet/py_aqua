from flask.cli import with_appcontext
import sys
import json
import click

from src.bo.base import BaseBO


class QuizCheckerCli():
    KEYS_SECTION = ['name', 'id', 'groups']
    KEYS_GROUP = ['name', 'id', 'description', 'items']
    KEYS_ITEM = ['question', 'id', 'type', 'analysis', 'reviewer']
    KEYS_ANALYSIS = ['category', 'priority']
    KEYS_REVIEWER_FULL = ['option', 'helper', 'status', 'score', 'review', 'remediation', 'short']
    KEYS_REVIEWER_BEST = ['option', 'helper', 'status', 'score', 'review']
    KEYS_REVIEWER_DISABLED = ['option', 'helper']

    REVIEW_DISABLED = BaseBO.REVIEW_DISABLED
    ITEM_TYPES = [
        BaseBO.ITEM_QCM_MULTIPLE,
        BaseBO.ITEM_QCM_UNIQUE,
        BaseBO.ITEM_TABLE_DOUBLE,
        BaseBO.ITEM_TABLE_SIMPLE,
        BaseBO.ITEM_FREE_TEXT,
    ]

    def __init__(self, logger, mapping_bo, title, quiz, analysis):
        self.__logger = logger
        self.__title = title
        self.__quiz = quiz
        self.__analysis = analysis
        self.__mapping_bo = mapping_bo

    def init_app(self, app):
        app.cli.add_command(click.Command(
            name='check_quiz',
            callback=with_appcontext(self.check),
            params=[],
            help='Verify quiz configuration (ids unicity, keys, ...).',
        ))

    def check(self):
        categories = [category.get('id') for category in self.__analysis['categories']]
        priorities = [priority['label'] for priority in self.__analysis['priorities']]
        statuses = [status['label'] for status in self.__analysis['statuses']]
        score_ranges = {status: [] for status in statuses}

        for section in self.__quiz['sections']:
            print('[+] Checking section \'{}\' has (name, id, groups) keys ... '.format(section.get('id')), end='')
            errors = [key for key in self.KEYS_SECTION if key not in section]
            self.__print_errors(errors, 'missing key(s): ')

            for group in section['groups']:
                print(' | Checking group \'{}\' has (name, id, description, items) keys ... '.format(group.get('id')), end='')
                errors = [key for key in self.KEYS_GROUP if key not in group]
                self.__print_errors(errors, 'missing key(s): ')

                for item in group['items']:
                    print(' |   Checking item \'{}\' has (question, type, id, analysis, reviewer) keys ... '.format(item.get('id')), end='')
                    errors = [key for key in self.KEYS_ITEM if key not in item]
                    self.__print_errors(errors, 'missing key(s): ')

                    print(' |     Checking the analysis has (category, priority) keys ... ', end='')
                    analysis = item['analysis']
                    errors = [key for key in self.KEYS_ANALYSIS if key not in analysis]
                    self.__print_errors(errors, 'missing key(s): ')

                    print(' |     Checking reviewer options always have (option, helper, status, score, review, remediation, short) keys ')
                    reviewer = item['reviewer']
                    for review in reviewer:
                        print(' |       Checking option \'{}\' ... '.format(review['option']), end='')
                        expected = self.KEYS_REVIEWER_FULL
                        if review.get('status') == self.__analysis['best']['status']:
                            expected = self.KEYS_REVIEWER_BEST

                        if review.get('option') == self.REVIEW_DISABLED:
                            expected = self.KEYS_REVIEWER_DISABLED

                        errors = [key for key in expected if key not in review]
                        self.__print_errors(errors, 'missing key(s): ')

                        # score ranges
                        if review['option'] != self.REVIEW_DISABLED:
                            score_ranges[review['status']].append(str(review['score']))

                    print(' |     Checking type is in ({}) ... '.format(', '.join(self.ITEM_TYPES)), end='')
                    errors = []
                    if item['type'] not in self.ITEM_TYPES:
                        errors.append(item['type'])
                    self.__print_errors(errors, 'unknown type: ')

                    print(' |     Checking analysis category is in ({}) ... '.format(', '.join(categories)), end='')
                    errors = []
                    if analysis['category'] not in categories:
                        errors.append(analysis['category'])
                    self.__print_errors(errors, 'unknown category: ')

                    print(' |     Checking analysis priority is in ({}) ... '.format(', '.join(priorities)), end='')
                    errors = []
                    if analysis['priority'] not in priorities:
                        errors.append(analysis['priority'])
                    self.__print_errors(errors, 'unknown priority: ')

                    print(' |     Checking reviewer status are in ({}) ... '.format(', '.join(statuses)), end='')
                    errors = [review['status'] for review in reviewer if review['option'] != self.REVIEW_DISABLED and review['status'] not in statuses]
                    self.__print_errors(errors, 'unknown status: ')

                    print(' |     Checking reviewer score are float numbers ... ', end='')
                    errors = [str(type(review['score'])) for review in reviewer if review['option'] != self.REVIEW_DISABLED and not isinstance(review['score'], float)]
                    self.__print_errors(errors, 'invalid type: ')

            print('')

        print('[+] Checking ID unicity ... ', end='')
        duplicates = self.__mapping_bo.check_item_ids_unicity()
        if len(duplicates) > 0:
            print('\n| duplicates: {}'.format(', '.join(duplicates)))
        else:
            print('ok')

        print('')
        print('[+] For information, scores observed are:')
        for status, ranges in score_ranges.items():
            print(' | status \'{}\': {}'.format(status, ', '.join(set(ranges))))

        # display ok score range
        # display ko score range
        # display partial score range
        # check not_answered score range

    def __print_errors(self, errors, prefix):
        if len(errors) == 0:
            print('ok')
        else:
            print(prefix + ', '.join(errors))
            sys.exit(1)
