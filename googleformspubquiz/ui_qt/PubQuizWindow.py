import collections
import pathlib
from typing import Optional

from PyQt5 import uic
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QHeaderView, QFileDialog

from quiz import Quiz
from ui_qt.SectionWindow import SectionWindow
from ui_qt.TeamsWindow import TeamsWindow

uidir = pathlib.Path(__file__).parent


class PubQuizWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(uidir/'PubQuizWindow.ui', self)

        self.pubquiz = None     # type: Optional[Quiz]
        self.directory = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_directory)

        self.widget_sectiontable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.widget_leaderboard.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.widget_leaderboard.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

    def select_dir(self):
        self.timer.stop()
        self.directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.widget_pubquiz_dir.setText(self.directory)

        self.pubquiz = Quiz.load_dir_with_ini(self.directory)
        self.refresh()
        self.timer.start(3000)

    def fill_section_list(self):
        self.widget_sectiontable.setRowCount(len(self.pubquiz.sections))
        for row, section in enumerate(self.pubquiz.sections):
            self.widget_sectiontable.setItem(row, 0, QTableWidgetItem(section.name))
            score_item = QTableWidgetItem('{:.0f}'.format(section.fraction_of_correct_answers()*100))
            self.widget_sectiontable.setItem(row, 1, score_item)
            score_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

    def open_section(self, row, _column):
        section = self.pubquiz.sections[row]
        section_window = SectionWindow(section=section, directory=self.directory)
        section_window.exec_()
        self.refresh()

    def fill_leaderboard(self):
        leaderboard = list(self.pubquiz.leaderboard())
        self.widget_leaderboard.setRowCount(len(leaderboard))
        for row, (i, team, points) in enumerate(leaderboard):
            self.widget_leaderboard.setItem(row, 0, QTableWidgetItem(i))
            self.widget_leaderboard.setItem(row, 1, QTableWidgetItem(team))
            points_item = QTableWidgetItem(points)
            self.widget_leaderboard.setItem(row, 2, points_item)
            points_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

    def refresh(self):
        self.fill_section_list()
        self.fill_leaderboard()
        self.refresh_teams_label()

    def check_directory(self):
        self.pubquiz.update_from_dir(self.directory)
        self.refresh()

    def refresh_teams_label(self):
        counter = collections.Counter()
        for section in self.pubquiz.sections:
            for response in section.responses:
                counter[response.team] += 1

        incomplete = 0
        for team, count in counter.items():
            if count != len(self.pubquiz.sections):
                incomplete += 1

        self.label_team_problems.setText('{} teams have not answered all sections'.format(incomplete))

    def check_teams(self):
        teams_window = TeamsWindow(self.pubquiz)
        teams_window.exec_()
        self.refresh()
