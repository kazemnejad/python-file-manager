from PyQt4 import QtGui

from mainForm import Ui_MainWindow


class FileManager(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(FileManager, self).__init__()

        self.setupUi(self)
        self.show()

    def init_ui(self):
        pass
