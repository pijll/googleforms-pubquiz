from PyQt5.QtWidgets import QApplication

from ui.PubQuizWindow import PubQuizWindow

app = QApplication([])
mainwindow = PubQuizWindow()
mainwindow.show()
app.exec()
