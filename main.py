#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui

from filemanager import FileManager

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    fileManager = FileManager()
    fileManager.show()
    app.exec_()
