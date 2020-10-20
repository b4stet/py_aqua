class AnswersBo():
    ITEM_QCM_UNIQUE = 'qcm_unique'
    ITEM_QCM_MULTIPLE = 'qcm_multiple'
    ITEM_TABLE_SIMPLE = 'table_simple'
    ITEM_TABLE_DOUBLE = 'table_double'
    ITEM_FREE_TEXT = 'text'

    def __init__(self, logger, quiz):
        self.__logger = logger
        self.__quiz = quiz

    def assemble(self, answers):
        answers_summary = {}
        for section in self.__quiz['sections']:
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

                    answer = None
                    # for text, get the value
                    if item['type'] == self.ITEM_FREE_TEXT:
                        answer = answers[full_id].replace('_', ' ')

                    # for qcm_unique items, transform in 2 list: selected/other options
                    if item['type'] == self.ITEM_QCM_UNIQUE:
                        selected = answers[full_id]
                        other_options = [option for option in item['options'] if option != selected]
                        answer = [
                            'selected: {}'.format(selected).replace('_', ' '),
                            'other options: {}'.format(', '.join(other_options)).replace('_', ' '),
                        ]

                    # for qcm_multiple items, transform in 2 list: selected/not selected
                    if item['type'] == self.ITEM_QCM_MULTIPLE:
                        item_answers = [k for k in answers.keys() if k.startswith(full_id) and not k.endswith('-notes')]
                        selected = [answer.split('-')[-1] for answer in item_answers]
                        not_selected = [option for option in item['options'] if option not in selected]
                        answer = [
                            'selected: {}'.format(', '.join(selected)).replace('_', ' '),
                            'not selected: {}'.format(', '.join(not_selected)).replace('_', ' '),
                        ]

                    # for one entry tables, re-assemble header and rows
                    if item['type'] == self.ITEM_TABLE_SIMPLE:
                        answer = []
                        header = [column['title'] for column in item['columns']]
                        answer.append(header)

                        i = 0
                        row_id = '{}-l{}'.format(full_id, i)
                        row_answers = {k: v for k, v in answers.items() if k.startswith(row_id) and not k.endswith('-notes')}
                        while len(row_answers) > 0:
                            row = []
                            for col in item['columns']:
                                cell_id = '{}-{}'.format(row_id, col['id'])
                                # for text, get the value
                                if col['type'] == self.ITEM_FREE_TEXT:
                                    row.append(row_answers[cell_id].replace('_', ' '))

                                # for qcm_unique items, transform in 2 list: selected/other options
                                if col['type'] == self.ITEM_QCM_UNIQUE:
                                    selected = row_answers[cell_id]
                                    other_options = [option for option in col['options'] if option != selected]
                                    row.append([
                                        'selected: {}'.format(selected).replace('_', ' '),
                                        'other options: {}'.format(', '.join(other_options)).replace('_', ' '),
                                    ])

                                # for qcm_multiple items, transform in 2 list: selected/not selected
                                if col['type'] == self.ITEM_QCM_MULTIPLE:
                                    cell_answers = [k for k in row_answers.keys() if k.startswith(cell_id)]
                                    selected = [answer.split('-')[-1] for answer in cell_answers]
                                    not_selected = [option for option in col['options'] if option not in selected]
                                    row.append([
                                        'selected: {}'.format(', '.join(selected)).replace('_', ' '),
                                        'not selected: {}'.format(', '.join(not_selected)).replace('_', ' '),
                                    ])

                            answer.append(row)

                            # next row
                            i += 1
                            row_id = '{}-l{}'.format(full_id, i)
                            row_answers = {k: v for k, v in answers.items() if k.startswith(row_id)}

                    # for double entry tables, re-assemble header and rows, first column is second header
                    if item['type'] == self.ITEM_TABLE_DOUBLE:
                        answer = []
                        header = [column['title'] for column in item['columns']]
                        answer.append(header)

                        for row in item['rows']:
                            row_id = '{}-{}'.format(full_id, row.lower().replace(' ', '_'))
                            row_answers = {k: v for k, v in answers.items() if k.startswith(row_id) and not k.endswith('-notes')}
                            row_res = [row]

                            for col in item['columns'][1:]:
                                cell_id = '{}-{}'.format(row_id, col['id'])
                                # for text, get the value
                                if col['type'] == self.ITEM_FREE_TEXT:
                                    row_res.append(row_answers[cell_id].replace('_', ' '))

                                # for qcm_unique items, transform in 2 list: selected/other options
                                if col['type'] == self.ITEM_QCM_UNIQUE:
                                    selected = row_answers[cell_id]
                                    other_options = [option for option in col['options'] if option != selected]
                                    row_res.append([
                                        'selected: {}'.format(selected).replace('_', ' '),
                                        'other options: {}'.format(', '.join(other_options)).replace('_', ' '),
                                    ])

                                # for qcm_multiple items, transform in 2 list: selected/not selected
                                if col['type'] == self.ITEM_QCM_MULTIPLE:
                                    cell_answers = [k for k in row_answers.keys() if k.startswith(cell_id)]
                                    selected = [answer.split('-')[-1] for answer in cell_answers]
                                    not_selected = [option for option in col['options'] if option not in selected]
                                    row_res.append([
                                        'selected: {}'.format(', '.join(selected)).replace('_', ' '),
                                        'not selected: {}'.format(', '.join(not_selected)).replace('_', ' '),
                                    ])

                            answer.append(row_res)

                    answers_summary[sid]['groups'][gid]['answers'].append({
                        'item': item['question'],
                        'type': item['type'],
                        'answer': answer,
                    })
        return answers_summary
