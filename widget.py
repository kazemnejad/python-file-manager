import time
from PyQt4 import QtGui

from PyQt4.QtCore import pyqtSignal, Qt, QModelIndex
from PyQt4.QtGui import QTreeView, QWidget


class SuperTreeView(QTreeView):
    enterKeyPressed = pyqtSignal(QModelIndex)
    backspaceKeyPressed = pyqtSignal(QModelIndex)

    copyKeysPressed = pyqtSignal(QModelIndex)
    cutKeysPressed = pyqtSignal(QModelIndex)
    pasteKeysPressed = pyqtSignal(QModelIndex)
    findKeysPressed = pyqtSignal()

    def __init__(self, parent):
        super(SuperTreeView, self).__init__(parent)

        self.start_time = time.time()
        self.is_control_pressed = False

    def keyPressEvent(self, event):
        key = event.key()
        index = self.selectedIndexes()[0] if len(self.selectedIndexes()) > 0 else None

        if event.key() == Qt.Key_Control:
            self.start_time = time.time()
            self.is_control_pressed = True
        else:
            if self.is_control_pressed and (time.time() - self.start_time) < 0.5:
                if key == Qt.Key_C:
                    self.copyKeysPressed.emit(index)
                elif key == Qt.Key_X:
                    self.cutKeysPressed.emit(index)
                elif key == Qt.Key_V:
                    self.pasteKeysPressed.emit(index)
                elif key == Qt.Key_F:
                    self.findKeysPressed.emit()

                self.is_control_pressed = False
                event.accept()

                return
            else:
                self.is_control_pressed = False

            if key == Qt.Key_Return or key == Qt.Key_Enter:
                if index is not None:
                    self.enterKeyPressed.emit(index)
            elif key == Qt.Key_Backspace:
                self.backspaceKeyPressed.emit(index)
            else:
                return QTreeView.keyPressEvent(self, event)

        event.accept()

    def dragEnterEvent(self, event):
        event.acceptProposedAction()


class GoHappySystemTrayIcon(QtGui.QSystemTrayIcon):
    def __init__(self, parent=None):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("resources/gohappy.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        QtGui.QSystemTrayIcon.__init__(self, icon, parent)

        menu = QtGui.QMenu(parent)
        self.runAction = menu.addAction("Run Client")
        self.setContextMenu(menu)


class SuperCentralWidget(QtGui.QWidget):
    findKeysPressed = pyqtSignal()

    def __init__(self, parent):
        super(SuperCentralWidget, self).__init__(parent)

        self.start_time = time.time()
        self.is_control_pressed = False

    def keyPressEvent(self, event):
        key = event.key()

        if event.key() == Qt.Key_Control:
            self.start_time = time.time()
            self.is_control_pressed = True
        else:
            if self.is_control_pressed and (time.time() - self.start_time) < 0.5:
                if key == Qt.Key_F:
                    self.findKeysPressed.emit()

                self.is_control_pressed = False
                event.accept()

                return
            else:
                self.is_control_pressed = False

            return QWidget.keyPressEvent(self, event)

        event.accept()
