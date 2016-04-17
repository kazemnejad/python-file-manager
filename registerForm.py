# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Register.ui'
#
# Created: Sun Apr 17 15:29:05 2016
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

class Ui_RegisterWindow(object):
    def setupUi(self, RegisterWindow):
        RegisterWindow.setObjectName(_fromUtf8("RegisterWindow"))
        RegisterWindow.resize(375, 206)
        self.centralwidget = QtGui.QWidget(RegisterWindow)
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
        self.passwordEdit = QtGui.QLineEdit(self.centralwidget)
        self.passwordEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.passwordEdit.setObjectName(_fromUtf8("passwordEdit"))
        self.verticalLayout_4.addWidget(self.passwordEdit)
        self.passwordRepEdit = QtGui.QLineEdit(self.centralwidget)
        self.passwordRepEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.passwordRepEdit.setObjectName(_fromUtf8("passwordRepEdit"))
        self.verticalLayout_4.addWidget(self.passwordRepEdit)
        self.verticalLayout_3.addLayout(self.verticalLayout_4)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btnCancel = QtGui.QPushButton(self.centralwidget)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.horizontalLayout.addWidget(self.btnCancel)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.registerBtn = QtGui.QPushButton(self.centralwidget)
        self.registerBtn.setObjectName(_fromUtf8("registerBtn"))
        self.horizontalLayout.addWidget(self.registerBtn)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.verticalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        RegisterWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(RegisterWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 375, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        RegisterWindow.setMenuBar(self.menubar)

        self.retranslateUi(RegisterWindow)
        QtCore.QMetaObject.connectSlotsByName(RegisterWindow)
        RegisterWindow.setTabOrder(self.btnCancel, self.usernameEdit)
        RegisterWindow.setTabOrder(self.usernameEdit, self.passwordEdit)
        RegisterWindow.setTabOrder(self.passwordEdit, self.passwordRepEdit)
        RegisterWindow.setTabOrder(self.passwordRepEdit, self.registerBtn)

    def retranslateUi(self, RegisterWindow):
        RegisterWindow.setWindowTitle(_translate("RegisterWindow", "Register", None))
        self.label.setText(_translate("RegisterWindow", "Register", None))
        self.usernameEdit.setPlaceholderText(_translate("RegisterWindow", "Username", None))
        self.passwordEdit.setPlaceholderText(_translate("RegisterWindow", "Password", None))
        self.passwordRepEdit.setPlaceholderText(_translate("RegisterWindow", "Repeat Password", None))
        self.btnCancel.setText(_translate("RegisterWindow", "Cancel", None))
        self.registerBtn.setText(_translate("RegisterWindow", "Register", None))

