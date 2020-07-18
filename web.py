import os
from src import bootstrap

quiz_file = os.environ.get('AQUA_QUIZ', 'quiz_default.yml')

app = bootstrap(quiz_file=quiz_file)

if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=8080,
        threaded=True,
        debug='True',
    )
