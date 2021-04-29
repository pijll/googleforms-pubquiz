import flask_table
from flask import Blueprint, render_template, url_for
from flask_table import Col, Table, LinkCol

from ui_flask.util import get_quiz

pubquiz_page = Blueprint('pubquiz_page', __name__)


class SectionTable(Table):
    section_nr = Col('NR', show=False)
    quiz_name = Col('QUIZ', show=False)
    section_name = Col('NAME', show=False)
    section = LinkCol('Section', 'section_page.show', url_kwargs=dict(section_nr='section_nr', quiz_name='quiz_name'), attr='section_name')
    correct_pct = Col('% correct')


class LeaderboardTable(Table):
    position = Col('')
    team_name = Col('Team')
    points = Col('Points')


@pubquiz_page.route('/<quiz_name>/')
def show(quiz_name):
    quiz = get_quiz(quiz_name)
    sections = [
        {
            'section_nr': i,
            'quiz_name': quiz_name,
            'section_name': s.name,
            'correct_pct': '{:.0f}'.format(s.fraction_of_correct_answers()*100)
        } for i, s in enumerate(quiz.sections, start=1)]
    section_table = SectionTable(sections)

    teams = [{
        'position': position,
        'team_name': name,
        'points': score
    } for position, name, score in quiz.leaderboard()]
    team_table = LeaderboardTable(teams)

    return render_template('pubquizpage.html',
                           quiz_name=quiz_name,
                           section_table=section_table,
                           team_table=team_table)
