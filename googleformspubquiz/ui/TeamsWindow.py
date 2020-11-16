import collections
import pathlib

from PyQt5 import uic, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QTableWidgetItem

uidir = pathlib.Path(__file__).parent


class TeamsWindow(QDialog):
    def __init__(self, pubquiz):
        super().__init__()
        uic.loadUi(uidir/'TeamsWindow.ui', self)

        self.pubquiz = pubquiz
        self.show_teams()

    def show_teams(self):
        teams = self.pubquiz.teams
        sections = self.pubquiz.number_of_responses_per_section_per_team()

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

            teamname_item = QTableWidgetItem(team.name)
            teamname_item.setData(Qt.UserRole, team)
            teamname_item.setBackground(color)
            self.table_teams.setItem(row, 0, teamname_item)

            for col, (section, responded) in enumerate(sections[team].items(), start=1):
                item = QTableWidgetItem(str(responded))
                item.setBackground(color)
                self.table_teams.setItem(row, col, item)

        self.selection_changed()

    def selection_changed(self):
        can_merge = self.pubquiz.can_merge_teams(list(self.selected_teams()))
        self.button_merge_teams.setEnabled(can_merge)

    def merge_teams(self):
        teams_to_merge = list(self.selected_teams())
        self.pubquiz.merge_teams(teams_to_merge)
        self.show_teams()

    def selected_teams(self):
        selection_model = self.table_teams.selectionModel()
        for row in selection_model.selectedRows():
            row_number = row.row()
            team = self.table_teams.item(row_number, 0).data(Qt.UserRole)
            yield team
