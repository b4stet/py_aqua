from flask.cli import with_appcontext
import io
import sys
import base64
import click
from docx.shared import Cm
from docxtpl import DocxTemplate, InlineImage


class ReportGeneratorCli():
    def __init__(self, logger, mapping_bo, analysis_bo, answers_bo):
        self.__logger = logger
        self.__mapping_bo = mapping_bo
        self.__analysis_bo = analysis_bo
        self.__answers_bo = answers_bo

    def init_app(self, app):
        options = [
            click.Option(
                ['--review', '-r'],
                help='[required] Review file, in json format.'
            ),
            click.Option(
                ['--output', '-o'],
                help='[required] Output docx file name.'
            ),
        ]

        app.cli.add_command(click.Command(
            name='generate_report',
            callback=with_appcontext(self.generate),
            params=options,
            help='Generate docx report from a review file.',
        ))

    def generate(self, review=None, output=None):
        # validate inputs
        if review is None:
            print('Missing argument --review.')
            sys.exit(1)

        if output is None:
            print('Missing argument --output.')
            sys.exit(1)
