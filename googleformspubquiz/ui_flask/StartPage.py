from flask import Blueprint, url_for, render_template

from ui_flask.util import pubquiz_dir

main_page = Blueprint('main_page', __name__)


@main_page.route('/')
def show():
    quizzes = [(q.name, url_for('pubquiz_page.show', quiz_name=q.name))
               for q in pubquiz_dir.iterdir()]
    return render_template('startpage.html',
                           quizzes=quizzes)
