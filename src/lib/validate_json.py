import json


def validate(content, quiz_title, quiz_version):
    # check key/values
    try:
        assert 'quiz-version' in content.keys(), 'No key "quiz-version" found.'
        assert 'quiz-name' in content.keys(), 'No key "quiz-name" found.'
        for key, value in content.items():
            assert isinstance(key, str), 'Expected str keys. Got {}'.format(type(value))
            assert isinstance(value, str), 'Expected str values. Got {}'.format(type(value))
    except Exception as err:
        raise

    # compare config
    if content['quiz-name'] != quiz_title:
        raise ValueError('Quiz mismatch. Running "{}" config but file is for "{}".'.format(
            quiz_title, content['quiz-name']
        ))

    # compare versions
    if content['quiz-version'] != quiz_version:
        raise ValueError('Version mismatch. Running v{} but file has v{}. Do convert file beforehand.'.format(
            quiz_version, content['quiz-version']
        ))
