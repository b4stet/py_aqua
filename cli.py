import os
from src import bootstrap_cli

app_config = os.environ.get('AQUA_APP', 'config/app_default.yml')
quiz_config = os.environ.get('AQUA_QUIZ', 'config/quiz_default.yml')

app = bootstrap_cli(app_config=app_config, quiz_config=quiz_config)
