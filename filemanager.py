import os
import shutil
import subprocess
import sys
import threading
from PyQt4 import QtGui
from gi.repository import Notify, GdkPixbuf

import re
from PyQt4.QtCore import QDir, QFileInfo, QSize, QFileSystemWatcher, Qt
from PyQt4.QtGui import QFileSystemModel, QHeaderView, QPalette, QMenu, QAction, QProgressDialog, QStandardItemModel, \
    QStandardItem, QFileIconProvider, QMessageBox

from NewConnectionForm import Ui_NewConnectionWindow
from findForm import Ui_FindWindow
from gohappy import GoHappy
from gohappygenerics import AuthResponceCode, PathResult
from loginForm import Ui_LoginWindow
from mainForm import Ui_mainWindow
from registerForm import Ui_RegisterWindow
from search import Searcher
from widget import GoHappySystemTrayIcon


class Find(QtGui.QMainWindow, Ui_FindWindow):
    def __init__(self, callback, current_path, parent=None):
        super(Find, self).__init__(parent)

        self.setupUi(self)
        move_to_center_of_parent(parent, self)

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


class LoginWindow(QtGui.QMainWindow, Ui_LoginWindow):
    def __init__(self, parent, callback):
        super(LoginWindow, self).__init__(parent)

        self.setupUi(self)
        move_to_center_of_parent(parent, self)

        self.btnCancel.pressed.connect(self.close)
        self.passwordEdit.returnPressed.connect(self.on_login_clicked)
        self.loginBtn.pressed.connect(self.on_login_clicked)

        self.successful_login_listener = callback

    def on_login_clicked(self):
        username = str(self.usernameEdit.text())
        password = str(self.passwordEdit.text())

        if len(username) == 0 or len(password) == 0:
            return
        self.username = username
        GoHappy.login(username, password, self.on_result_received)
        self.loginBtn.setEnabled(False)

    def on_result_received(self, result, msg, token):
        if result:
            if result == AuthResponceCode.SUCCESS and token:
                GoHappy.save_token(token)
                self.close()
                self.successful_login_listener(self.username)
            elif result == AuthResponceCode.FAIL:
                self.label.setText("Login Failed")


class RegisterWindow(QtGui.QMainWindow, Ui_RegisterWindow):
    def __init__(self, parent, callback):
        super(RegisterWindow, self).__init__(parent)

        self.setupUi(self)
        move_to_center_of_parent(parent, self)

        self.btnCancel.pressed.connect(self.close)
        self.passwordRepEdit.returnPressed.connect(self.on_register_clicked)
        self.registerBtn.pressed.connect(self.on_register_clicked)

        self.successful_login_listener = callback

    def on_register_clicked(self):
        username = str(self.usernameEdit.text())
        password = str(self.passwordEdit.text())
        passwordRep = str(self.passwordRepEdit.text())
        if len(username) == 0 or len(password) == 0 or len(passwordRep) == 0 or password != passwordRep:
            return
        self.username = username
        GoHappy.register(username, password, self.on_result_received)
        self.registerBtn.setEnabled(False)

    def on_result_received(self, result, msg, token, user_id):
        if result:
            if result == AuthResponceCode.SUCCESS and token:
                GoHappy.save_token(token)
                self.close()
                self.successful_login_listener(self.username)
            elif result == AuthResponceCode.FAIL:
                self.label.setText("Register Failed")


class NewConnection(QtGui.QMainWindow, Ui_NewConnectionWindow):
    def __init__(self, parent, callback):
        super(NewConnection, self).__init__(parent)
        self.setupUi(self)

        self.move(parent.frameGeometry().topLeft() + parent.rect().center() - self.rect().center())
        self.new_exploration_listener = callback

        self.btnCancel.pressed.connect(self.close)
        self.connectBtn.pressed.connect(self.on_connect_clicked)

    def on_connect_clicked(self):
        username = str(self.usernameEdit.text())

        if len(username) == 0:
            return

        self.new_exploration_listener(username)
        self.close()


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
        self.init_menu()

        self.gohappy = None
        self.session_id = None
        self.exploration_progress_bar = None
        self.source_username = None
        self.remote_model = None
        self.is_remote = False
        self.remote_cache = {}

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

        self.loginAction = QAction('Login', self)
        self.loginAction.triggered.connect(self.on_login)
        self.loginAction.setShortcut('F11')
        self.loginAction.setStatusTip('Login To GoHappy')

        self.registerAction = QAction('Register', self)
        self.registerAction.triggered.connect(self.on_register)
        self.registerAction.setShortcut('F12')
        self.registerAction.setStatusTip('Register In GoHappy')

        self.logOutAction = QAction('LogOut', self)
        self.logOutAction.triggered.connect(self.on_logOut)

        self.connectAction = QAction('New Exploration', self)
        self.connectAction.triggered.connect(self.on_user_asked_new_connection)
        self.connectAction.setEnabled(False)

    def init_menu(self):
        menubar = self.menuBar()
        self.mainMenu = menubar.addMenu('GoHappy')
        self.mainMenu.addAction(self.loginAction)
        self.mainMenu.addAction(self.registerAction)

    def on_right_pane_item_clicked(self, index):
        data = index.data(9).toPyObject()
        if self.is_remote:
            self.load_remote(data)
            return

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
        if self.is_remote: return

        path = self.leftPaneFileModel.filePath(index)
        self.enter_dir(self.rightPane, self.rightPaneFileModel, path, FileManager.NORMAL, True)

    def on_back(self, event):
        if self.current_index == 0: return

        pth = str(self.history[self.current_index - 1])
        if self.is_remote:
            if pth in self.remote_cache:
                self.load_from_cache(pth)
                self.current_index -= 1

                self.update_indicator()
                return

        self.enter_dir(self.rightPane, self.rightPaneFileModel,
                       self.history[self.current_index - 1], FileManager.BACK, False)

    def on_forward(self, event):
        if self.current_index == len(self.history) - 1: return

        pth = str(self.history[self.current_index + 1])
        if self.is_remote:
            if pth in self.remote_cache:
                self.load_from_cache(pth)
                self.current_index += 1

                self.update_indicator()
                return

        self.enter_dir(self.rightPane, self.rightPaneFileModel,
                       self.history[self.current_index + 1], FileManager.FORWARD, False)

    def on_dir_changed(self, path):
        if path != self.history[self.current_index]: return

        rootIndex = self.rightPaneFileModel.setRootPath(path)
        self.rightPane.setRootIndex(rootIndex)

        # index = self.leftPaneFileModel.index(path)
        # self.leftPaneFileModel.emit()

    def on_copy_keys_pressed(self, index):
        if self.is_remote: return

        path = str(self.rightPaneFileModel.filePath(index))
        self.on_copy(path)

    def on_cut_keys_pressed(self, index):
        if self.is_remote: return

        path = str(self.rightPaneFileModel.filePath(index))
        self.on_cut(path)

    def on_paste_keys_pressed(self, index):
        if self.is_remote: return

        self.on_paste(None)

    def on_find_keys_pressed(self):
        if self.is_remote: return

        current_path = self.history[self.current_index]

        w = Find(self.on_search_result_received, current_path, self)
        w.show()

    def make_treeview_with_list(self, list, text, is_folder, data, model):
        iconProvider = QFileIconProvider()
        parent = model.invisibleRootItem()
        for i in list:
            item = QStandardItem()
            item.setText(i[text])
            item.setData(i, data)
            item.setIcon(iconProvider.icon(QFileIconProvider.Folder if i[is_folder] else QFileIconProvider.File))
            item.setEditable(False)
            parent.appendRow(item)
        return parent

    def on_search_result_received(self, result):
        self.search_model = QStandardItemModel()
        result.sort(reverse=True, key=lambda x: x[-1])
        parent = self.make_treeview_with_list(result, 1, -2, 9, self.search_model)
        self.rightPane.setModel(self.search_model)
        self.rightPane.setRootIndex(parent.index())

    def on_login(self):
        loginWindow = LoginWindow(self, self.on_successful_login)
        loginWindow.show()

    def on_register(self):
        regWindow = RegisterWindow(self, self.on_successful_login)
        regWindow.show()

    def create_logOut_menu(self, username):
        self.logoutMenu = self.menuBar().addMenu(username)
        self.logoutMenu.addAction(self.connectAction)
        self.logoutMenu.addAction(self.logOutAction)

    def on_user_asked_new_connection(self):
        w = NewConnection(self, self.start_new_exploration)
        w.show()

    def on_successful_login(self, username):
        self.menubar.clear()
        self.create_logOut_menu(username)

        self.gohappy = GoHappy(GoHappy.load_token(), self.on_ready_listener)

    def on_logOut(self):
        GoHappy.delete_token()
        self.menubar.clear()
        self.init_menu()

    def update_left_pane(self, path, enterType):
        leftIndex = self.leftPaneFileModel.index(path, 0)
        self.expand_children(leftIndex, self.leftPane, enterType)

    def update_watcher(self, path):
        self.watcher.removePaths(self.watcher.directories())
        self.watcher.addPath(path)

    def update_indicator(self):
        currentPath = str(self.history[self.current_index])
        res = re.match(r'(\/home\/.*?\/).*', currentPath)

        what_to_replace = QDir.homePath()
        if res:
            what_to_replace = res.group(1)

        if currentPath.startswith('/home'):
            currentPath = currentPath.replace(what_to_replace, "Home/")
        elif currentPath == "home":
            currentPath = "Home"

        self.pathIndicator.setText(currentPath)

    def open_menu(self, position):
        if self.is_remote: return

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

    # GoHappy Server
    def on_ready_listener(self, instance):
        self.gohappy.start_new_connection(self.on_new_connection_result)

    def on_new_connection_result(self, is_successful):
        if not is_successful:
            self.gohappy.start_new_connection(self.on_new_connection_result)
            return

        self.connectAction.setEnabled(True)

    def start_new_exploration(self, username):
        if not self.gohappy.is_new_connection_opened:
            return

        self.gohappy.start_new_exploration(username, self.on_new_exploration_result)

        self.source_username = username
        self.exploration_progress_bar = self.create_progress_bar(self)
        self.exploration_progress_bar.exec_()

    def on_new_exploration_result(self, session_id, is_successful, is_source_offline, is_permission_denied):
        if is_successful and session_id:
            self.session_id = str(session_id)
            self.leftPane.setEnabled(False)
            self.is_remote = True
            show_notification('Exploration started!', 'Exploring ' + self.source_username)

            self.gohappy.get_files(self.session_id, 'home', self.on_file_request_result)

            self.history = []
            self.current_index = -1
        else:
            if self.exploration_progress_bar:
                self.exploration_progress_bar.close()

            msg = 'Sorry, Unable to connect :('
            if is_source_offline:
                msg = 'Sorry, ' + self.source_username + ' is offline :('
            elif is_permission_denied:
                msg = 'Sorry, ' + self.source_username + ' reject your request'

            self.show_error_message(msg)

    def on_file_request_result(self, is_successful, error, data, session_id, is_source_offline, pth):
        if self.exploration_progress_bar:
            self.exploration_progress_bar.close()

        if is_successful or len(data) > 0:
            self.remote_cache[pth] = data

            self.remote_model = QStandardItemModel()
            parent = self.make_treeview_with_list(data, 0, 2, 9, self.remote_model)
            self.rightPane.setModel(self.remote_model)
            self.rightPane.setRootIndex(parent.index())

            self.history.append(pth)
            self.current_index += 1

            self.update_indicator()
        else:
            msg = 'Sorry, Unable to fetch new data, please try again :('
            if error == PathResult.ACCESS_DENIED:
                msg = 'Unable to reach to asked location try again'
            elif error == PathResult.NOT_FOUND:
                msg = 'Path not found'

            self.show_error_message(msg)

    def load_remote(self, data):
        if not data \
                or not self.is_remote \
                or not self.session_id \
                or not self.gohappy \
                or not self.gohappy.is_new_connection_opened:
            return

        try:
            path = str(data[1])
            is_dir = bool(data[2])
        except:
            return

        if not is_dir:
            return

        if path in self.remote_cache:
            self.load_from_cache(path)
            self.history.append(path)
            self.current_index += 1

            self.update_indicator()
            return

        self.gohappy.get_files(self.session_id, path, self.on_file_request_result)

        if not self.exploration_progress_bar:
            self.exploration_progress_bar = self.create_progress_bar(self)
        self.exploration_progress_bar.exec_()

    def load_from_cache(self, pth):
        if not pth in self.remote_cache:
            return

        data = self.remote_cache.get(pth, [])
        self.remote_model = QStandardItemModel()
        parent = self.make_treeview_with_list(data, 0, 2, 9, self.remote_model)
        self.rightPane.setModel(self.remote_model)
        self.rightPane.setRootIndex(parent.index())

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

    @staticmethod
    def create_progress_bar(parent):
        progressbar = QProgressDialog(parent)
        progressbar.setWindowTitle("Please wait...")
        progressbar.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        progressbar.setCancelButton(None)
        progressbar.setModal(True)
        progressbar.setRange(0, 0)
        move_to_center_of_parent(parent, progressbar)
        return progressbar

    @staticmethod
    def show_error_message(msg):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("Something goes wrong")
        msgBox.setText(msg)
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.setDefaultButton(QMessageBox.Ok)
        msgBox.show()


def move_to_center_of_parent(parent, child):
    child.move(parent.window().frameGeometry().topLeft() + parent.window().rect().center() - child.rect().center())


def show_notification(title, body):
    Notify.init("Gohappy client")
    notification = Notify.Notification.new(title, body)

    image = GdkPixbuf.Pixbuf.new_from_file("resources/gohappy.svg")

    notification.set_icon_from_pixbuf(image)
    notification.set_image_from_pixbuf(image)

    return notification.show()


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
