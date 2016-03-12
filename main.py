#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt4 import QtGui
import sys

from filemanager import FileManager

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    fileManager = FileManager()
    app.exec_()
