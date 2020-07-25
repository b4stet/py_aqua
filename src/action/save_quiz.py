from flask import request, send_file
import yaml
import io

from src.action.base import BaseAction


class SaveQuizAction(BaseAction):
    def post(self):
        data = request.form

        answers = {}
        for key, value in data.items():
            answers.update({key: value})

        memory = io.BytesIO()
        memory.write(yaml.safe_dump(answers, default_flow_style=False, default_style="'").encode('utf-8'))
        memory.seek(0)

        return send_file(memory, mimetype='application/yaml', as_attachment=True, attachment_filename='answers.yml')
