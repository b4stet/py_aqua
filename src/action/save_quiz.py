from flask import request, send_file
import json
import io

from src.action.base import BaseAction


class SaveQuizAction(BaseAction):
    def post(self):
        data = request.form
        memory = io.BytesIO()
        memory.write(json.dumps(data, skipkeys=True, ensure_ascii=True, indent=2).encode('utf-8'))
        memory.seek(0)

        return send_file(memory, mimetype='application/json', as_attachment=True, attachment_filename='answers.json')
