from flask.cli import with_appcontext
import json
import click


class QuizListerCli():
    OUTPUT_FORMAT = ['csv', 'json']

    def __init__(self, logger, title, quiz):
        self.__logger = logger
        self.__title = title
        self.__quiz = quiz

    def init_app(self, app):
        options = [
            click.Option(
                ['--output'],
                help='Format to output result. Default is json',
                default='json',
                type=click.Choice(self.OUTPUT_FORMAT)
            ),
        ]

        app.cli.add_command(click.Command(
            name='list_quiz',
            callback=with_appcontext(self.list),
            params=options,
            help='List quiz items (question, category, priority).',
        ))

    def list(self, output):
        items = []
        for section in self.__quiz['sections']:
            sid = section['id']
            for group in section['groups']:
                gid = group['id']
                for item in group['items']:
                    iid = item['id']
                    analysis = item['analysis']
                    items.append({
                        'section_id': sid,
                        'group_id': gid,
                        'item_id': iid,
                        'category': analysis['category'],
                        'priority': analysis['priority'],
                        'question': item['question'],
                    })

        if output == 'json':
            print(json.dumps(items))

        if output == 'csv':
            columns = ['section_id', 'group_id', 'item_id', 'category', 'priority', 'question']
            print(','.join(columns))
            for item in items:
                values = [item[col] for col in columns]
                print(','.join(str(value) for value in values))
