import collections
import pathlib
from typing import Optional

from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem

from googleformspubquiz import Section
from quiz import Quiz
from ui.SectionWindow import SectionWindow

uidir = pathlib.Path(__file__).parent


class PubQuizWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(uidir/'PubQuizWindow.ui', self)

        self.pubquiz = None     # type: Optional[Quiz]
        self.directory = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_directory)

    def select_dir(self):
        self.timer.stop()
        # directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.directory = r'/home/pijll/PycharmProjects/GoogleFormsPubquiz/tests/testdata'
        self.widget_pubquiz_dir.setText(self.directory)

        self.pubquiz = Quiz.load_dir(self.directory)
        self.refresh()
        self.timer.start(3000)

    def fill_section_list(self):
        self.widget_sectiontable.setRowCount(len(self.pubquiz.sections))
        for row, section in enumerate(self.pubquiz.sections):
            self.widget_sectiontable.setItem(row, 0, QTableWidgetItem(section.name))
            self.widget_sectiontable.setItem(row, 1, QTableWidgetItem('{:.0f}'.format(section.fraction_of_correct_answers()*100)))

    def open_section(self, row, column):
        section = self.pubquiz.sections[row]
        section_window = SectionWindow(section=section)
        section_window.exec_()
        self.refresh()

    def fill_leaderboard(self):
        leaderboard = list(self.pubquiz.leaderboard())
        self.widget_leaderboard.setRowCount(len(leaderboard))
        for row, (i, team, points) in enumerate(leaderboard):
            self.widget_leaderboard.setItem(row, 0, QTableWidgetItem(i))
            self.widget_leaderboard.setItem(row, 1, QTableWidgetItem(team))
            self.widget_leaderboard.setItem(row, 2, QTableWidgetItem(points))

    def refresh(self):
        self.fill_section_list()
        self.fill_leaderboard()
        self.refresh_teams_label()

    def check_directory(self):
        for p in pathlib.Path(self.directory).iterdir():
            if p.is_file() and p.suffix == '.csv':
                section_name = p.stem
                section = self.pubquiz.get_section(section_name)
                if not section:
                    with p.open() as infile:
                        section = Section.read_csv(infile, name=section_name)
                    self.pubquiz.sections.append(section)

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
        pass
