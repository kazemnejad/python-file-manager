from PyQt4 import QtGui

from PyQt4.QtCore import QDir, QFileInfo
from PyQt4.QtGui import QFileSystemModel, QHeaderView, QPalette

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
        colorName = self.palette().color(QPalette.ToolTipText).name()
        self.leftPane.setStyleSheet("background-color: " + str(colorName))

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
        self.rightPane.doubleClicked.connect(self.on_right_pane_item_clicked)

        self.rightPane.header().setStretchLastSection(False)
        self.rightPane.header().setMovable(False)
        self.rightPane.header().setResizeMode(0, QHeaderView.Stretch)

    def on_right_pane_item_clicked(self, index):
        path = self.rightPaneFileModel.filePath(index)

        self.enter_dir(self.rightPane, self.rightPaneFileModel, path)
        if QFileInfo(path).isDir():
            index = self.leftPaneFileModel.index(path, 0)
            self.expand_children(index, self.leftPane)

    def enter_dir(self, pane, model, path):
        rootIndex = model.setRootPath(path)
        pane.setRootIndex(rootIndex)

    def expand_children(self, index, pane):
        if not index.isValid():
            return

        childCount = index.model().rowCount(index)
        for i in xrange(0, childCount):
            child = index.child(i, 0)
            self.expand_children(child, pane)

        if not pane.isExpanded(index):
            pane.expand(index)
