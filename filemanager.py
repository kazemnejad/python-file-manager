import os
import subprocess
from PyQt4 import QtGui

import sys
from PyQt4.QtCore import QDir, QFileInfo
from PyQt4.QtGui import QFileSystemModel, QHeaderView, QPalette

from mainForm import Ui_mainWindow


class FileManager(QtGui.QMainWindow, Ui_mainWindow):
    NORMAL = 0
    FORWARD = 1
    BACK = 2

    def __init__(self):
        super(FileManager, self).__init__()

        self.setupUi(self)

        self.history = [QDir.homePath()]
        self.current_index = 0

        self.init_actions()
        self.init_file_system_model()
        self.init_left_pane()
        self.init_right_pane()

        print self.history

    def init_file_system_model(self):
        self.leftPaneFileModel = QFileSystemModel(self.leftPane)
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
        self.rightPane.setItemsExpandable(False)
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
            self.enter_dir(self.rightPane, self.rightPaneFileModel, path, FileManager.NORMAL, False)
        elif fileInfo.isFile():
            self.open_file(path)

    def on_left_pane_item_clicked(self, index):
        path = self.leftPaneFileModel.filePath(index)
        self.enter_dir(self.rightPane, self.rightPaneFileModel, path, FileManager.NORMAL, True)

    def on_back(self, event):
        if self.current_index == 0: return
        self.enter_dir(self.rightPane, self.rightPaneFileModel,
                       self.history[self.current_index - 1], FileManager.BACK, False)

    def on_forward(self, event):
        if self.current_index == len(self.history) - 1: return
        self.enter_dir(self.rightPane, self.rightPaneFileModel,
                       self.history[self.current_index + 1], FileManager.FORWARD, False)

    def update_left_pane(self, path, enterType):
        leftIndex = self.leftPaneFileModel.index(path, 0)
        self.expand_children(leftIndex, self.leftPane, enterType)

    def enter_dir(self, pane, model, path, enterType, is_from_left_pane):
        rootIndex = model.setRootPath(path)
        pane.setRootIndex(rootIndex)

        if enterType == FileManager.NORMAL:
            if not is_from_left_pane:
                self.update_left_pane(path, FileManager.NORMAL)

            if self.history[self.current_index] == path:
                return

            del self.history[self.current_index + 1:]
            self.history.append(path)
            self.current_index += 1
        elif enterType == FileManager.FORWARD:
            self.update_left_pane(path, enterType)
            self.current_index += 1
        elif enterType == FileManager.BACK:
            self.update_left_pane(self.history[self.current_index], enterType)
            self.current_index -= 1

        print self.history

    def expand_children(self, index, pane, enterType):
        if not index.isValid():
            return

        # childCount = index.model().rowCount(index)
        # for i in xrange(0, childCount):
        #     child = index.child(i, 0)
        #     self.expand_children(child, pane, enterType)

        if enterType == FileManager.BACK:
            pane.collapse(index)
        else:
            if not pane.isExpanded(index):
                pane.expand(index)

    def open_file(self, filepath):
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', filepath))
        elif os.name == 'nt':
            os.startfile(filepath)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', filepath))
