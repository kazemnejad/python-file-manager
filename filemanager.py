import os
import subprocess
from PyQt4 import QtGui

import sys
from PyQt4.QtCore import QDir, QFileInfo
from PyQt4.QtGui import QFileSystemModel, QHeaderView, QPalette

from mainForm import Ui_mainWindow


class FileManager(QtGui.QMainWindow, Ui_mainWindow):
    def __init__(self):
        super(FileManager, self).__init__()

        self.setupUi(self)

        self.history = [QDir.homePath()]
        self.current_index = 0

        self.init_file_system_model()
        self.init_left_pane()
        self.init_right_pane()
        self.init_actions()

    def init_file_system_model(self):
        # self.mFileSystemModel = QFileSystemModel(self.leftPane)
        self.leftPaneFileModel = QFileSystemModel(self)
        self.leftPaneFileModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)

        self.rightPaneFileModel = QFileSystemModel(self)

    def init_left_pane(self):
        rootIndex = self.leftPaneFileModel.setRootPath(QDir.homePath())
        self.leftPane.setModel(self.leftPaneFileModel)
        self.leftPane.setRootIndex(rootIndex)
        self.leftPane.doubleClicked.connect(self.on_left_pane_item_clicked)
        colorName = self.palette().color(QPalette.Window).name()
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

    def init_actions(self):
        self.tbActionBack.triggered.connect(self.on_back)
        self.tbActionForward.triggered.connect(self.on_forward)

    def on_right_pane_item_clicked(self, index):
        path = self.rightPaneFileModel.filePath(index)
        fileInfo = QFileInfo(path)
        if fileInfo.isDir():
            self.enter_dir(self.rightPane, self.rightPaneFileModel, path)

            leftIndex = self.leftPaneFileModel.index(path, 0)
            self.expand_children(leftIndex, self.leftPane)
        elif fileInfo.isFile():
            self.open_file(path)

    def on_left_pane_item_clicked(self, index):
        path = self.leftPaneFileModel.filePath(index)
        self.enter_dir(self.rightPane, self.rightPaneFileModel, path)

    def on_back(self, event):
        print "OnBack"

    def on_forward(self, event):
        print "OnForward"

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

    def open_file(self, filepath):
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', filepath))
        elif os.name == 'nt':
            os.startfile(filepath)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', filepath))
