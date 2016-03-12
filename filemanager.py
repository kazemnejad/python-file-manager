from PyQt4.QtGui import QWidget


class FileManager(QWidget):
    def __init__(self):
        super(FileManager, self).__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('GoHappy FileManager')
        self.show()
