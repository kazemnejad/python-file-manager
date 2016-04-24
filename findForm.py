# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Find.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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


class Ui_FindWindow(object):
    def setupUi(self, FindWindow):
        FindWindow.setObjectName(_fromUtf8("FindWindow"))
        FindWindow.resize(514, 132)
        self.centralwidget = QtGui.QWidget(FindWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.queryEdit = QtGui.QLineEdit(self.centralwidget)
        self.queryEdit.setObjectName(_fromUtf8("lineEdit"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.queryEdit)
        self.label_3 = QtGui.QLabel(self.centralwidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.label_3)
        self.verticalLayout.addLayout(self.formLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.btnCancel = QtGui.QPushButton(self.centralwidget)
        self.btnCancel.setObjectName(_fromUtf8("pushButton_2"))
        self.horizontalLayout_2.addWidget(self.btnCancel)
        self.btnFind = QtGui.QPushButton(self.centralwidget)
        self.btnFind.setObjectName(_fromUtf8("pushButton"))
        self.horizontalLayout_2.addWidget(self.btnFind)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout.addLayout(self.verticalLayout)
        FindWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(FindWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 514, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        FindWindow.setMenuBar(self.menubar)

        self.retranslateUi(FindWindow)
        QtCore.QMetaObject.connectSlotsByName(FindWindow)

    def retranslateUi(self, FindWindow):
        FindWindow.setWindowTitle(_translate("FindWindow", "Find in files", None))
        self.label.setText(_translate("FindWindow", "Pattern", None))
        self.label_3.setText(
                _translate("FindWindow", "Ex: Should && ... || Should Not && ... || Better && ... || Type/Kind", None))
        self.btnCancel.setText(_translate("FindWindow", "Cancel", None))
        self.btnFind.setText(_translate("FindWindow", "Find", None))
