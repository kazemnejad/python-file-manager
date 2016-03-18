import time
from PyQt4.QtCore import pyqtSignal, Qt, QModelIndex
from PyQt4.QtGui import QTreeView


class SuperTreeView(QTreeView):
    enterKeyPressed = pyqtSignal(QModelIndex)
    backspaceKeyPressed = pyqtSignal(QModelIndex)

    copyKeysPressed = pyqtSignal(QModelIndex)
    cutKeysPressed = pyqtSignal(QModelIndex)
    pasteKeysPressed = pyqtSignal(QModelIndex)

    def __init__(self, parent):
        super(SuperTreeView, self).__init__(parent)

        self.start_time = time.time()
        self.is_control_pressed = False

    def keyPressEvent(self, event):
        key = event.key()
        index = self.selectedIndexes()[0]

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
