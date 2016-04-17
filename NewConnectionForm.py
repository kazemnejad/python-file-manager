# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Connect.ui'
#
# Created: Sun Apr 17 19:15:25 2016
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

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

class Ui_NewConnectionWindow(object):
    def setupUi(self, NewConnectionWindow):
        NewConnectionWindow.setObjectName(_fromUtf8("NewConnectionWindow"))
        NewConnectionWindow.resize(375, 140)
        self.centralwidget = QtGui.QWidget(NewConnectionWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.label = QtGui.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_3.addWidget(self.label)
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.usernameEdit = QtGui.QLineEdit(self.centralwidget)
        self.usernameEdit.setObjectName(_fromUtf8("usernameEdit"))
        self.verticalLayout_4.addWidget(self.usernameEdit)
        self.verticalLayout_3.addLayout(self.verticalLayout_4)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btnCancel = QtGui.QPushButton(self.centralwidget)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.horizontalLayout.addWidget(self.btnCancel)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.connectBtn = QtGui.QPushButton(self.centralwidget)
        self.connectBtn.setObjectName(_fromUtf8("connectBtn"))
        self.horizontalLayout.addWidget(self.connectBtn)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.verticalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        NewConnectionWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(NewConnectionWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 375, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        NewConnectionWindow.setMenuBar(self.menubar)

        self.retranslateUi(NewConnectionWindow)
        QtCore.QMetaObject.connectSlotsByName(NewConnectionWindow)
        NewConnectionWindow.setTabOrder(self.btnCancel, self.usernameEdit)
        NewConnectionWindow.setTabOrder(self.usernameEdit, self.connectBtn)

    def retranslateUi(self, NewConnectionWindow):
        NewConnectionWindow.setWindowTitle(_translate("NewConnectionWindow", "New Connection to GoHappy user", None))
        self.label.setText(_translate("NewConnectionWindow", "Who?", None))
        self.usernameEdit.setPlaceholderText(_translate("NewConnectionWindow", "a GoHappy Username", None))
        self.btnCancel.setText(_translate("NewConnectionWindow", "Cancel", None))
        self.connectBtn.setText(_translate("NewConnectionWindow", "Connect", None))

