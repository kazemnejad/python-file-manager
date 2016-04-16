import os
import shutil
import subprocess
import sys
import threading
from PyQt4 import QtGui

from PyQt4.QtCore import QDir, QFileInfo, QSize, QFileSystemWatcher, Qt, pyqtSignal
from PyQt4.QtGui import QFileSystemModel, QHeaderView, QPalette, QMenu, QAction, QProgressDialog, QStandardItemModel, \
    QStandardItem, QFileIconProvider

from findForm import Ui_FindWindow
from gohappy import GoHappy
from mainForm import Ui_mainWindow
from search import Searcher
from widget import GoHappySystemTrayIcon


class Find(QtGui.QMainWindow, Ui_FindWindow):
    def __init__(self, callback, current_path, parent=None):
        super(Find, self).__init__(parent)

        self.setupUi(self)

        self.listener_callback = callback
        self.path = str(current_path)

        self.setWindowTitle("Search in " + self.path)

        self.btnFind.pressed.connect(self.on_find_pressed)
        self.btnCancel.pressed.connect(self.on_cancel_pressed)
        self.queryEdit.returnPressed.connect(self.on_find_pressed)

        self.progressbar = QProgressDialog(self)
        self.progressbar.setWindowTitle("Please wait...")
        self.progressbar.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.progressbar.setCancelButton(None)
        self.progressbar.setModal(True)
        self.progressbar.setRange(0, 0)

    def on_cancel_pressed(self):
        self.close()

    def on_find_pressed(self):
        query = str(self.queryEdit.text())
        if len(query) == 0:
            return

        print self.path

        searcher = Searcher(self.path, query, self.on_finished)
        searcher.search()

        searcher.updateSignal.connect(self.on_finished)

        self.progressbar.exec_()

    def on_finished(self, results):
        self.progressbar.cancel()
        self.progressbar.close()

        self.close()
        self.listener_callback(results)


class FileManager(QtGui.QMainWindow, Ui_mainWindow):
    NORMAL = 0
    FORWARD = 1
    BACK = 2
    FLAGCOPY = 0
    SRC = ''

    def __init__(self):
        super(FileManager, self).__init__()

        self.setupUi(self)

        self.history = [QDir.homePath()]
        self.current_index = 0
        self.update_indicator()

        self.watcher = QFileSystemWatcher()
        self.watcher.addPath(QDir.homePath())
        self.watcher.directoryChanged.connect(self.on_dir_changed)

        self.init_actions()
        self.init_file_system_model()
        self.init_left_pane()
        self.init_right_pane()
        self.init_tray_icon()

    def init_tray_icon(self):
        self.trayIcon = GoHappySystemTrayIcon()
        self.trayIcon.runAction.triggered.connect(lambda event: GoHappy.run_client())
        self.trayIcon.show()

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

        self.rightPane.setAlternatingRowColors(True)
        self.rightPane.updatesEnabled()
        self.rightPane.setIconSize(QSize(32, 32))

        self.rightPane.setContextMenuPolicy(Qt.CustomContextMenu)
        self.rightPane.customContextMenuRequested.connect(self.open_menu)

        self.rightPane.header().setStretchLastSection(False)
        self.rightPane.header().setMovable(False)
        self.rightPane.header().setResizeMode(0, QHeaderView.Stretch)

        self.rightPane.enterKeyPressed.connect(self.on_right_pane_item_clicked)
        self.rightPane.backspaceKeyPressed.connect(self.on_back)

        self.rightPane.copyKeysPressed.connect(self.on_copy_keys_pressed)
        self.rightPane.cutKeysPressed.connect(self.on_cut_keys_pressed)
        self.rightPane.pasteKeysPressed.connect(self.on_paste_keys_pressed)
        self.rightPane.findKeysPressed.connect(self.on_find_keys_pressed)

        self.centralwidget.findKeysPressed.connect(self.on_find_keys_pressed)

    def init_actions(self):
        self.tbActionBack.triggered.connect(self.on_back)
        self.tbActionForward.triggered.connect(self.on_forward)

    def on_right_pane_item_clicked(self, index):
        data = index.data(9).toPyObject()
        if data:
            if not data[-2]:
                self.open_file(data[0])
            return

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

    def on_dir_changed(self, path):
        if path != self.history[self.current_index]: return

        rootIndex = self.rightPaneFileModel.setRootPath(path)
        self.rightPane.setRootIndex(rootIndex)

        # index = self.leftPaneFileModel.index(path)
        # self.leftPaneFileModel.emit()

    def on_copy_keys_pressed(self, index):
        path = str(self.rightPaneFileModel.filePath(index))
        self.on_copy(path)

    def on_cut_keys_pressed(self, index):
        path = str(self.rightPaneFileModel.filePath(index))
        self.on_cut(path)

    def on_paste_keys_pressed(self, index):
        self.on_paste(None)

    def on_find_keys_pressed(self):
        current_path = self.history[self.current_index]

        w = Find(self.on_search_result_received, current_path, self)
        w.show()

    def on_search_result_received(self, result):
        self.search_model = QStandardItemModel()
        parent = self.search_model.invisibleRootItem()

        iconProvider = QFileIconProvider()
        result.sort(reverse=True, key=lambda x: x[-1])
        for i in result:
            item = QStandardItem()
            item.setText(i[1])
            item.setData(i, 9)
            item.setIcon(iconProvider.icon(QFileIconProvider.Folder if i[-2] else QFileIconProvider.File))
            item.setEditable(False)

            parent.appendRow(item)

        self.rightPane.setModel(self.search_model)
        self.rightPane.setRootIndex(parent.index())

    def update_left_pane(self, path, enterType):
        leftIndex = self.leftPaneFileModel.index(path, 0)
        self.expand_children(leftIndex, self.leftPane, enterType)

    def update_watcher(self, path):
        self.watcher.removePaths(self.watcher.directories())
        self.watcher.addPath(path)

    def update_indicator(self):
        currentPath = str(self.history[self.current_index])
        if currentPath.startswith(str(QDir.homePath())):
            currentPath = currentPath.replace(str(QDir.homePath()), "Home")

        self.pathIndicator.setText(currentPath)

    def open_menu(self, position):
        menu = QMenu()

        # get clicked item file path by its mouse position
        index = self.rightPane.indexAt(position)
        path = self.rightPaneFileModel.filePath(index)

        # cut
        cutAction = QAction("Cut", menu)
        cutAction.triggered.connect(lambda event: self.on_cut(str(path)))
        menu.addAction(cutAction)

        # copy
        copyAction = QAction("Copy", menu)
        copyAction.triggered.connect(lambda event: self.on_copy(str(path)))
        menu.addAction(copyAction)

        # paste
        if (self.FLAGCOPY != 0 and not (os.path.isfile(str(path)))):
            pasteAction = QAction("Paste", menu)
            pasteAction.triggered.connect(lambda event: self.on_paste(str(path)))
            menu.addAction(pasteAction)

        # delete
        deleteAction = QAction("Delete", menu)
        deleteAction.triggered.connect(lambda event: self.on_delete(str(path)))
        menu.addAction(deleteAction)

        # NewFolder
        newFolderAction = QAction("NewFolder", menu)
        newFolderAction.triggered.connect(lambda event: self.on_newFolder(str(path)))
        menu.addAction(newFolderAction)

        menu.exec_(self.rightPane.viewport().mapToGlobal(position))

    def on_cut(self, path):
        self.FLAGCOPY = 2
        self.SRC = path
        print path

    def on_copy(self, path):
        self.FLAGCOPY = 1
        self.SRC = path
        print path

    def on_paste(self, dst):
        if dst is None or len(dst) == 0:
            dst = str(self.history[self.current_index])
        if self.FLAGCOPY == 1:
            t = threading.Thread(target=MyCopy(self.SRC, dst))
        elif self.FLAGCOPY == 2:
            t = threading.Thread(target=shutil.move(self.SRC, dst))
        t.start()
        print dst

    def on_delete(self, src):
        if os.path.isfile(src):
            os.remove(src)
        else:
            shutil.rmtree(src)
        print src

    def on_newFolder(self, dst):
        if dst is None or len(dst) == 0:
            dst = str(self.history[self.current_index])
        hel = "newFolder"
        print "hel : ", hel
        if not os.path.isdir(os.path.join(dst, hel)):
            os.mkdir(os.path.join(dst, hel))
        else:
            count = 1
            while os.path.isdir(os.path.join(dst, hel + str(count))):
                print "count : ", count
                count += 1
            print "Dst : ", os.path.join(dst, hel + str(count))
            os.mkdir(os.path.join(dst, hel + str(count)))

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

        self.update_indicator()
        self.update_watcher(path)
        # print self.history

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


def MyCopy(src, dst):
    print "src : ", src, " dst : ", dst
    print "name :", os.path.basename(src)
    if os.path.isfile(src):
        shutil.copy2(src, dst)
    if not os.path.isdir(os.path.join(dst, os.path.basename(src))):
        os.mkdir(os.path.join(dst, os.path.basename(src)))
    print "befor : ", dst
    hel = os.path.join(dst, os.path.basename(src))
    dst = hel
    print "after : ", dst

    for file in os.listdir(src):
        print "\t i : ", file
        if os.path.isfile(os.path.join(src, file)):
            shutil.copy2(os.path.join(src, file), dst)
        else:
            print "\t\t dst : ", os.path.join(dst, file), os.path.isdir(os.path.join(dst, file))
            if not os.path.isdir(os.path.join(dst, file)):
                os.mkdir(os.path.join(dst, file))
            MyCopy(os.path.join(src, file), os.path.join(dst, file))
