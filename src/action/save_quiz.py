from flask import request, send_file
import json
import io
from datetime import datetime

from src.action.base import BaseAction


class SaveQuizAction(BaseAction):
    def __init__(self, logger, mode):
        super().__init__(logger)
        self.__mode = mode

    def post(self):
        data = request.form
        memory = io.BytesIO()
        memory.write(json.dumps(data, skipkeys=True, ensure_ascii=True, indent=2).encode('utf-8'))
        memory.seek(0)

        now = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = 'answers.json'
        if self.__mode == self.MODE_REVIEWER:
            filename = 'review.json'
        filename = now + '_' + filename

        return send_file(memory, mimetype='application/json', as_attachment=True, attachment_filename=filename)
