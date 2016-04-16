#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore

from filemanager import FileManager

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)

    fileManager = FileManager()
    fileManager.show()
    app.exec_()
