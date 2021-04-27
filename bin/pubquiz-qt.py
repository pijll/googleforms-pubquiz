from PyQt5.QtWidgets import QApplication

from ui_qt.PubQuizWindow import PubQuizWindow

app = QApplication([])
mainwindow = PubQuizWindow()
mainwindow.show()
app.exec()
