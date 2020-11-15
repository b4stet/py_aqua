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
                ['--template', '-t'],
                help='[required] Docx template to use.'
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

    def generate(self, review=None, template=None, output=None):
        # validate inputs
        print('[+] Validating json file ...')
        if review is None:
            print('Missing argument --review.')
            sys.exit(1)

        if output is None:
            print('Missing argument --output.')
            sys.exit(1)

        if template is None:
            print('Missing argument --template.')
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
        analysis_sections, analysis_categories = self.__analysis_bo.analyze(review, mapping, waffle_borders=True)
        summary = self.__analysis_bo.summarize(analysis_sections, analysis_categories, mapping, waffle_borders=True)
        appendix = self.__answers_bo.assemble(answers)

        # convert b64 plots to docx stream
        document = DocxTemplate(template)
        summary['plot_grade_final'] = self.__b64_to_image(summary['plot_grade_final'], document, 5)
        summary['plot_grades_categories'] = self.__b64_to_image(summary['plot_grades_categories'], document, 7)
        summary['plot_grades_sections'] = self.__b64_to_image(summary['plot_grades_sections'], document, 7)
        summary['plot_soundness_items'] = self.__b64_to_image(summary['plot_soundness_items'], document, 10)

        for category in analysis_categories.values():
            category['plot_grade'] = self.__b64_to_image(category['plot_grade'], document, 4)
            category['plot_soundness'] = self.__b64_to_image(category['plot_soundness'], document, 10)

        # convert category descriptions (html) to text
        for category in analysis_config['categories']:
            category['description'] = self.__html_to_paragraph(category['description'])

        # convert group description (html) to text
        for sid, section_answers in appendix.items():
            for gid, group_answers in section_answers['groups'].items():
                group_answers['description'] = self.__html_to_paragraph(group_answers['description'])

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
        # because bs4 is crap with br tags
        html_cleaned = html.replace('<br/>', '')
        soup = BeautifulSoup(html_cleaned, 'html.parser').find_all(recursive=False)

        result = []
        for tag in soup:
            result += self.__process_tag(tag)
        return result

    def __process_tag(self, tag, depth=0):
        next_depth = depth
        if tag.name == 'ul':
            next_depth += 1

        children = tag.findChildren(recursive=False)
        result = []

        text = tag.find(text=True)
        if text is not None and text != '\n':
            result.append({
                'type': tag.name,
                'depth': depth,
                'content': text,
            })

        for child in children:
            result += self.__process_tag(child, next_depth)
        return result
