import flask_table
from flask import Blueprint, render_template, request, redirect, url_for
from flask_table import Col, LinkCol

from ui_flask.util import get_quiz

section_page = Blueprint('section_page', __name__)


class QuestionTable(flask_table.Table):
    quiz_name = Col('QUIZ', show=False)
    section_nr = Col('SECTION', show=False)
    question_nr = flask_table.Col('')
    question_text = flask_table.Col('Q', show=False)
    question = LinkCol('Question', 'question_page.show', url_kwargs=dict(quiz_name='quiz_name', section_nr='section_nr', question_nr='question_nr'), attr='question_text')
    correct_pct = flask_table.Col('% correct')


@section_page.route('/<quiz_name>/section/<int:section_nr>', methods=['GET', 'POST'])
def show(quiz_name, section_nr):
    quiz = get_quiz(quiz_name)
    section = quiz.sections[section_nr - 1]

    if request.method == 'POST':
        return redirect(url_for('pubquiz_page.show', quiz_name=quiz_name))

    questions = [
        {
            'quiz_name': quiz_name,
            'section_nr': section_nr,
            'question_nr': j,
            'question_text': shortened_section_name(q.name, int(j)),
            'correct_pct': '{:.0f}'.format(q.fraction_of_correct_responses()*100)
        } for j, q in enumerate(section.questions, start=1)]
    question_table = QuestionTable(questions)

    return render_template('sectionpage.html',
                           quiz=quiz_name,
                           section=section.name,
                           question_table=question_table)


def shortened_section_name(name, number):
    if name is None or name == '':
        return 'Question {}'.format(number)
    if len(name) >= 40:
        return name[:37] + '...'
    return name
