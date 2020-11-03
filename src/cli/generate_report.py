from flask.cli import with_appcontext
import io
import sys
import json
import base64
import click
from docx.shared import Cm, Mm
from docxtpl import DocxTemplate, InlineImage, RichText
from bs4 import BeautifulSoup

from src.lib import plot
from src.lib import validate_json


class ReportGeneratorCli():
    def __init__(self, logger, mapping_bo, analysis_bo, answers_bo, title, quiz):
        self.__logger = logger
        self.__mapping_bo = mapping_bo
        self.__analysis_bo = analysis_bo
        self.__answers_bo = answers_bo
        self.__title = title
        self.__quiz = quiz

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
        print('[+] Validating json file ...')
        if review is None:
            print('Missing argument --review.')
            sys.exit(1)

        if output is None:
            print('Missing argument --output.')
            sys.exit(1)

        try:
            with open(review, mode='r') as f:
                content = json.load(f)

            validate_json.validate(content, self.__title['short'], self.__quiz['version'])
            answers, review = self.__analysis_bo.extract_review(content)
        except Exception as err:
            raise
            sys.exit(1)

        # analyze
        print('[+] Performing the gap analysis ...')
        mapping = {
            'sections_id_name': {section['id']: section['name'] for section in self.__quiz['sections']},
            'items_by_full_id': self.__mapping_bo.map_items_by_full_id(),
            'scoring_by_grade': self.__mapping_bo.map_by_key('scoring', 'grade'),
            'statuses_by_label': self.__mapping_bo.map_by_key('statuses', 'label'),
            'priorities_by_label': self.__mapping_bo.map_by_key('priorities', 'label'),
            'categories_by_id': self.__mapping_bo.map_by_key('categories', 'id'),
        }

        analysis_config = self.__analysis_bo.get_analysis_config()
        analysis_sections, analysis_categories = self.__analysis_bo.analyze(review, mapping)
        summary = self.__analysis_bo.summarize(analysis_sections, analysis_categories, mapping)
        appendix = self.__answers_bo.assemble(answers)

        # convert b64 plots to docx stream
        document = DocxTemplate(analysis_config['docx_template'])
        summary['donut_result'] = self.__b64_to_image(summary['donut_result'], document, 5)
        summary['donut_categories'] = self.__b64_to_image(summary['donut_categories'], document, 7)
        summary['lollipop_sections'] = self.__b64_to_image(summary['lollipop_sections'], document, 15)
        summary['waffle_items'] = self.__b64_to_image(summary['waffle_items'], document, 15)

        for category in analysis_categories.values():
            category['donut_result'] = self.__b64_to_image(category['donut_result'], document, 5)
            category['waffle_items'] = self.__b64_to_image(category['waffle_items'], document, 15)

        # convert category descriptions (html) to rich text
        for category in analysis_config['categories']:
            category['description'] = self.__html_to_paragraph(category['description'])

        # fill docx
        print('[+] Filling docx report ...')
        context = {
            'page_break': RichText('\f'),
            'title': self.__title['long'],
            'analysis_config': analysis_config,
            'summary': summary,
            'categories': analysis_categories,
            'appendix': appendix,
        }
        document.render(context)
        document.save(output)
        print('[+] Report saved in {}'.format(output))

    def __b64_to_image(self, data, document, width):
        buffer = io.BytesIO()
        buffer.write(base64.b64decode(data))
        buffer.seek(0)
        return InlineImage(document, buffer, width=Cm(width))

    def __html_to_paragraph(self, html):
        soup = BeautifulSoup(html, 'html.parser').find_all()
        result = []
        for tag in soup:
            if tag.name == 'p' and tag.parent.name != 'p':
                result.append({
                    'type': 'paragraph',
                    'content': tag.text,
                })
            elif tag.name == 'li' and tag.parent.name != 'li':
                result.append({
                    'type': 'list',
                    'content': tag.text,
                })
        return result
