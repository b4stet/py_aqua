import os
from src import bootstrap

app_config = os.environ.get('AQUA_APP', 'config/app_default.yml')
quiz_config = os.environ.get('AQUA_QUIZ', 'config/quiz_default.yml')
mode = os.environ.get('AQUA_MODE', 'user')

app = bootstrap(app_config=app_config, quiz_config=quiz_config, mode=mode)

if __name__ == '__main__':
    app.run(
        host=app.config['host'],
        port=app.config['port'],
        threaded=True,
    )
