from PyQt4 import QtGui

from PyQt4.QtCore import QDir
from PyQt4.QtGui import QFileSystemModel

from mainForm import Ui_MainWindow


class FileManager(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(FileManager, self).__init__()

        self.setupUi(self)

        self.init_tree_View()

    def init_ui(self):
        pass


    def init_tree_View(self):
        self.mFileSystemModel = QFileSystemModel(self.treeView)
        rootIndex = self.mFileSystemModel.setRootPath(QDir.homePath())

        self.treeView.setModel(self.mFileSystemModel)
        self.treeView.setRootIndex(rootIndex)