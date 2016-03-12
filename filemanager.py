from PyQt4 import QtGui

from PyQt4.QtCore import QDir
from PyQt4.QtGui import QFileSystemModel, QHeaderView

from mainForm import Ui_mainWindow


class FileManager(QtGui.QMainWindow, Ui_mainWindow):
    def __init__(self):
        super(FileManager, self).__init__()

        self.setupUi(self)

        self.init_file_system_model()
        self.init_left_pane()
        self.init_right_pane()

    def init_file_system_model(self):
        # self.mFileSystemModel = QFileSystemModel(self.leftPane)
        self.leftPaneFileModel = QFileSystemModel(self)
        self.leftPaneFileModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)

        self.rightPaneFileModel = QFileSystemModel(self)

    def init_left_pane(self):
        rootIndex = self.leftPaneFileModel.setRootPath(QDir.homePath())
        self.leftPane.setModel(self.leftPaneFileModel)
        self.leftPane.setRootIndex(rootIndex)

        for columnIndex in xrange(1, self.leftPaneFileModel.columnCount()):
            self.leftPane.hideColumn(columnIndex)

        self.leftPane.setHeaderHidden(True)
        self.leftPane.resizeColumnToContents(0)

    def init_right_pane(self):
        rootIndex = self.rightPaneFileModel.setRootPath(QDir.homePath())

        self.rightPane.setModel(self.rightPaneFileModel)
        self.rightPane.setRootIndex(rootIndex)
        self.rightPane.setStyleSheet("QTreeView::branch {  border-image: url(none.png); }")
        self.rightPane.setExpandsOnDoubleClick(False)

        self.rightPane.header().setStretchLastSection(False)
        self.rightPane.header().setResizeMode(0, QHeaderView.Stretch)
