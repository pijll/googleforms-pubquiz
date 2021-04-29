from flask import Blueprint, redirect, render_template, request, url_for
import flask_table

from ui_flask import util
from ui_flask.util import get_quiz

question_page = Blueprint('question_page', __name__)


class CheckboxCol(flask_table.Col):
    def td_contents(self, i, attr_list):
        return '<input type="checkbox" value="{}" name="chkbxs" {}>'.format(i['answer'], 'checked' if i['correct'] else '')


class AnswerTable(flask_table.Table):
    correct = flask_table.BoolCol('IS_CORRECT', show=False)
    answer = flask_table.Col('Answer')
    count = flask_table.Col('Count')
    correct_checkbox = CheckboxCol('Correct')

    def get_tr_attrs(self, item):
        if item['correct']:
            return {'class': 'correct'}
        else:
            return {'class': 'incorrect'}


@question_page.route('/<quiz_name>/section/<int:section_nr>/question/<int:question_nr>', methods=['GET', 'POST'])
def show(quiz_name, section_nr, question_nr):
    quiz = get_quiz(quiz_name)
    section = quiz.sections[section_nr-1]
    question = section.questions[question_nr-1]

    if request.method == 'POST':
        return handle_post_method(quiz_name, section, question, request.form)
    else:
        return show_question(quiz_name=quiz_name, section=section, question=question)


def handle_post_method(quiz_name, section, question, request_form):
    question_nr = question.number_in_section
    section_nr = section.number_in_quiz
    new_correct_answers = request_form.getlist('chkbxs')
    if set(new_correct_answers) != question.correct_answers:
        question.correct_answers = request_form.getlist('chkbxs')
        section.save_answers(util.pubquiz_dir / quiz_name)
    if 'previous' in request_form:
        return redirect(url_for('question_page.show', quiz_name=quiz_name, section_nr=section_nr, question_nr=question_nr-1))
    elif 'next' in request_form:
        return redirect(url_for('question_page.show', quiz_name=quiz_name, section_nr=section_nr, question_nr=question_nr+1))
    elif 'close' in request_form:
        return redirect(url_for('section_page.show', quiz_name=quiz_name, section_nr=section_nr))
    elif 'save' in request_form:
        return show_question(quiz_name=quiz_name, section=section, question=question)


def show_question(quiz_name, section, question):
    question_nr = question.number_in_section

    answers = sorted([{'answer': a,
                       'correct': a in question.correct_answers,
                       'count': ct}
                      for a, ct in question.answer_list().items()],
                     key=lambda x: (-x['count'], x['answer']))

    answer_table = AnswerTable(answers)
    return render_template('questionpage.html',
                           quiz=quiz_name,
                           section=section.name,
                           question_nr=question_nr,
                           last_question = (question == section.questions[-1]),
                           question_text=question.name,
                           answer_table=answer_table,
                           correct='{:.0f}'.format(question.fraction_of_correct_responses()*100))
