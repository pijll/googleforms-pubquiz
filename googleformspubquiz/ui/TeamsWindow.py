import collections
import pathlib

from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtWidgets import QDialog, QTableWidgetItem

uidir = pathlib.Path(__file__).parent


class TeamsWindow(QDialog):
    def __init__(self, pubquiz):
        super().__init__()
        uic.loadUi(uidir/'TeamsWindow.ui', self)

        self.pubquiz = pubquiz
        self.show_teams()

    def show_teams(self):
        teams = self.pubquiz.teams()
        sections = self.pubquiz.sections_per_team()

        self.table_teams.setRowCount(len(teams))
        self.table_teams.setColumnCount(len(self.pubquiz.sections) + 1)

        for col, section in enumerate(self.pubquiz.sections, start=1):
            header = QTableWidgetItem(section.name)
            self.table_teams.setHorizontalHeaderItem(col, header)

        for row, team in enumerate(teams):
            responded_to_all_section = all(x for x in sections[team].values())
            if responded_to_all_section:
                color = QtGui.QColor(200, 255, 200)
            else:
                color = QtGui.QColor(255, 200, 200)

            teamname_item = QTableWidgetItem(team)
            teamname_item.setBackground(color)
            self.table_teams.setItem(row, 0, teamname_item)

            for col, (section, responded) in enumerate(sections[team].items(), start=1):
                item = QTableWidgetItem(str(responded))
                item.setBackground(color)
                self.table_teams.setItem(row, col, item)

        self.selection_changed()

    def selection_changed(self):
        if len(list(self.selected_teams())) <= 1:
            self.button_merge_teams.setEnabled(False)
            return

        sections_answered = collections.Counter()
        sections = self.pubquiz.sections_per_team()
        for team in self.selected_teams():
            for section, responded in sections[team].items():
                sections_answered[section] += int(responded)

        max_number_of_answers_per_question = max(sections_answered.values())

        self.button_merge_teams.setEnabled(max_number_of_answers_per_question <= 1)

    def merge_teams(self):
        teams_to_merge = list(self.selected_teams())
        new_name = teams_to_merge[0]

        for team in teams_to_merge[1:]:
            for section in self.pubquiz.sections:
                section.change_team_name(team, new_name)

        self.show_teams()

    def selected_teams(self):
        selection_model = self.table_teams.selectionModel()
        for row in selection_model.selectedRows():
            row_number = row.row()
            team_name = self.table_teams.item(row_number, 0).text()
            yield team_name
