import os
import pathlib

from googleformspubquiz import Quiz

default_dir = pathlib.Path(os.environ['HOME']) / 'pubquiz'
pubquiz_dir = pathlib.Path(os.environ.get('PUBQUIZ_DIR', default_dir))

def get_quiz(quiz_name):
    return Quiz.load_dir(pubquiz_dir / quiz_name, teamid_column=2, teamname_column=1)
