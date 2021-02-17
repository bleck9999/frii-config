# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'window.ui'
##
## Created by: Qt User Interface Compiler version 6.0.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(661, 526)
        self.addButton = QPushButton(Form)
        self.addButton.setObjectName(u"addButton")
        self.addButton.setGeometry(QRect(270, 130, 101, 22))
        self.path = QLineEdit(Form)
        self.path.setObjectName(u"path")
        self.path.setGeometry(QRect(20, 30, 601, 22))
        self.remote = QLineEdit(Form)
        self.remote.setObjectName(u"remote")
        self.remote.setGeometry(QRect(20, 100, 601, 22))
        self.checkBox = QCheckBox(Form)
        self.checkBox.setObjectName(u"checkBox")
        self.checkBox.setGeometry(QRect(20, 70, 131, 20))
        self.checkBox.setChecked(True)
        self.apply = QPushButton(Form)
        self.apply.setObjectName(u"apply")
        self.apply.setGeometry(QRect(570, 490, 80, 22))
        self.table = QTableWidget(Form)
        if (self.table.columnCount() < 2):
            self.table.setColumnCount(2)
        self.table.setObjectName(u"table")
        self.table.setGeometry(QRect(10, 170, 641, 311))
        font = QFont()
        font.setFamily(u"Monospace")
        self.table.setFont(font)
        self.table.setWordWrap(False)
        self.table.setRowCount(0)
        self.table.setColumnCount(2)
        self.table.horizontalHeader().setDefaultSectionSize(80)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setDefaultSectionSize(20)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.addButton.setText(QCoreApplication.translate("Form", u"Add repository", None))
        self.path.setText(QCoreApplication.translate("Form", u"Enter repository path here", None))
        self.remote.setText(QCoreApplication.translate("Form", u"Enter repository URL here", None))
        self.checkBox.setText(QCoreApplication.translate("Form", u"Clone repository", None))
        self.apply.setText(QCoreApplication.translate("Form", u"Apply", None))
    # retranslateUi

