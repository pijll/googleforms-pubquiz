from flask import Flask

from ui_flask.StartPage import main_page
from ui_flask.PubQuizPage import pubquiz_page
from ui_flask.SectionPage import section_page
from ui_flask.QuestionPage import question_page

app = Flask(__name__)
app.register_blueprint(main_page)
app.register_blueprint(pubquiz_page)
app.register_blueprint(section_page)
app.register_blueprint(question_page)


