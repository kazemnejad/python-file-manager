from PyQt4.QtCore import pyqtSignal, Qt, QModelIndex
from PyQt4.QtGui import QTreeView


class SuperTreeView(QTreeView):

    enterKeyPressed = pyqtSignal(QModelIndex)
    backspaceKeyPressed = pyqtSignal(QModelIndex)

    def __init__(self, parent):
        super(SuperTreeView, self).__init__(parent)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            index = self.selectedIndexes()[0]
            if index is not None:
                self.enterKeyPressed.emit(index)
                event.accept()
        elif event.key() == Qt.Key_Backspace:
            index = self.selectedIndexes()[0]
            self.backspaceKeyPressed.emit(index)
            event.accept()
        else:
            QTreeView.keyPressEvent(self, event)
