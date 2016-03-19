# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

from PyQt4.QtGui import QPalette, QLineEdit

from widget import SuperTreeView

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8


    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Ui_mainWindow(object):
    def setupUi(self, mainWindow):
        mainWindow.setObjectName(_fromUtf8("mainWindow"))
        mainWindow.setWindowModality(QtCore.Qt.NonModal)
        mainWindow.resize(960, 600)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("resources/gohappy.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        mainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(mainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(5, 5, 0, 0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.leftPane = QtGui.QTreeView(self.centralwidget)
        self.leftPane.setMinimumSize(QtCore.QSize(225, 0))
        self.leftPane.setMaximumSize(QtCore.QSize(225, 16777215))
        self.leftPane.setAutoFillBackground(False)
        self.leftPane.setFrameShape(QtGui.QFrame.NoFrame)
        self.leftPane.setLineWidth(0)
        self.leftPane.setObjectName(_fromUtf8("leftPane"))
        self.horizontalLayout.addWidget(self.leftPane)
        self.rightPane = SuperTreeView(self.centralwidget)
        self.rightPane.setFrameShape(QtGui.QFrame.StyledPanel)
        self.rightPane.setLineWidth(0)
        self.rightPane.setObjectName(_fromUtf8("rightPane"))
        self.horizontalLayout.addWidget(self.rightPane)
        spacerItem = QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        mainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(mainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 960, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        mainWindow.setMenuBar(self.menubar)
        self.toolBar = QtGui.QToolBar(mainWindow)
        self.toolBar.setMovable(False)
        self.toolBar.setAllowedAreas(QtCore.Qt.TopToolBarArea)
        self.toolBar.setFloatable(True)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        mainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.tbActionBack = QtGui.QAction(mainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("back"))
        self.tbActionBack.setIcon(icon)
        self.tbActionBack.setObjectName(_fromUtf8("tbActionBack"))
        self.tbActionForward = QtGui.QAction(mainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("forward"))
        self.tbActionForward.setIcon(icon)
        self.tbActionForward.setObjectName(_fromUtf8("tbActionForward"))
        self.toolBar.addAction(self.tbActionBack)
        self.toolBar.addAction(self.tbActionForward)

        self.pathIndicator = QLineEdit(self.toolBar)
        self.pathIndicator.setEnabled(False)
        self.toolBar.addWidget(self.pathIndicator)

        colorName = self.toolBar.palette().color(QPalette.Window).name()
        self.toolBar.setStyleSheet("background-color: " + str(colorName))

        self.retranslateUi(mainWindow)
        QtCore.QMetaObject.connectSlotsByName(mainWindow)

    def retranslateUi(self, mainWindow):
        mainWindow.setWindowTitle(_translate("mainWindow", "GoHappy FileManager", None))
        self.toolBar.setWindowTitle(_translate("mainWindow", "toolBar", None))
        self.tbActionBack.setText(_translate("mainWindow", "Back", None))
        self.tbActionBack.setToolTip(_translate("mainWindow", "Back", None))
        self.tbActionForward.setText(_translate("mainWindow", "Forward", None))
        self.tbActionForward.setShortcut(_translate("mainWindow", "Ctrl+Right", None))
