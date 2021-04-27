import pathlib

from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QHeaderView

uidir = pathlib.Path(__file__).parent


class SectionWindow(QDialog):
    def __init__(self, section, directory=None):
        super().__init__()
        uic.loadUi(uidir/'SectionWindow.ui', self)

        self.directory = directory
        self.section = section
        self.widget_section_name.setText(section.name)

        self.widget_answer_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        self.answer_info = None
        self.current_question = 0
        self.go_to_question(0)

    def previous_section(self):
        self.go_to_question(self.current_question - 1)

    def next_section(self):
        self.go_to_question(self.current_question + 1)

    def go_to_question(self, n):
        self.current_question = n
        question = self.section.questions[n]
        self.widget_question_label.setText(question.name)
        self.button_previous.setEnabled(n > 0)
        self.button_next.setEnabled(n < len(self.section.questions) - 1)

        percentage_correct = question.fraction_of_correct_responses() * 100
        self.label_percentage_correct.setText('{:.0f}% correct'.format(percentage_correct))

        self.widget_answer_table.clearContents()
        self.widget_answer_table.setSortingEnabled(False)

        answers = question.answer_list()
        self.widget_answer_table.setRowCount(len(answers))

        self.answer_info = []

        self.widget_answer_table.blockSignals(True)
        for row, (answer, count) in enumerate(sorted(answers.items(), key=lambda x: (-x[1], x[0]))):
            is_correct = answer in question.correct_answers
            if is_correct:
                color = QtGui.QColor(200, 255, 200)
            else:
                color = QtGui.QColor(255, 200, 200)

            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            checkbox_item.setCheckState(QtCore.Qt.Checked if answer in question.correct_answers else QtCore.Qt.Unchecked)
            checkbox_item.setBackground(color)
            self.widget_answer_table.setItem(row, 0, checkbox_item)

            answer_item = QTableWidgetItem(answer)
            answer_item.setBackground(color)
            self.widget_answer_table.setItem(row, 1, answer_item)

            count_item = QTableWidgetItem(str(count))
            count_item.setBackground(color)
            self.widget_answer_table.setItem(row, 2, count_item)

            self.answer_info.append([question, answer])

        self.widget_answer_table.setSortingEnabled(True)
        self.widget_answer_table.blockSignals(False)

    def cell_changed(self, row, column):
        question, answer = self.answer_info[row]
        checked = self.widget_answer_table.item(row, column).checkState()
        if checked:
            question.add_correct_answer(answer)
        else:
            question.remove_correct_answer(answer)
        self.go_to_question(self.current_question)

    def close_window(self):
        self.section.save_answers(self.directory)
        self.accept()
