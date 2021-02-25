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
        Form.resize(661, 576)
        self.addButton = QPushButton(Form)
        self.addButton.setObjectName(u"addButton")
        self.addButton.setGeometry(QRect(280, 190, 61, 22))
        self.path = QLineEdit(Form)
        self.path.setObjectName(u"path")
        self.path.setGeometry(QRect(20, 100, 601, 22))
        self.remote = QLineEdit(Form)
        self.remote.setObjectName(u"remote")
        self.remote.setGeometry(QRect(20, 160, 601, 22))
        self.checkBox = QCheckBox(Form)
        self.checkBox.setObjectName(u"checkBox")
        self.checkBox.setGeometry(QRect(20, 130, 131, 20))
        self.checkBox.setChecked(True)
        self.apply = QPushButton(Form)
        self.apply.setObjectName(u"apply")
        self.apply.setGeometry(QRect(570, 550, 80, 21))
        self.table = QTableWidget(Form)
        if (self.table.columnCount() < 2):
            self.table.setColumnCount(2)
        self.table.setObjectName(u"table")
        self.table.setGeometry(QRect(10, 230, 641, 311))
        font = QFont()
        font.setFamily(u"Monospace")
        self.table.setFont(font)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setDragEnabled(False)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setWordWrap(False)
        self.table.setRowCount(0)
        self.table.setColumnCount(2)
        self.table.horizontalHeader().setDefaultSectionSize(80)
        self.table.horizontalHeader().setProperty("showSortIndicator", False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setDefaultSectionSize(21)
        self.delentry = QPushButton(Form)
        self.delentry.setObjectName(u"delentry")
        self.delentry.setEnabled(False)
        self.delentry.setGeometry(QRect(10, 550, 80, 21))
        self.cancel = QPushButton(Form)
        self.cancel.setObjectName(u"cancel")
        self.cancel.setGeometry(QRect(480, 550, 80, 21))
        self.changeButton = QPushButton(Form)
        self.changeButton.setObjectName(u"changeButton")
        self.changeButton.setGeometry(QRect(20, 60, 81, 21))
        self.configlabel = QLabel(Form)
        self.configlabel.setObjectName(u"configlabel")
        self.configlabel.setGeometry(QRect(20, 10, 101, 17))
        self.textBrowser = QTextBrowser(Form)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setGeometry(QRect(20, 30, 601, 21))
        self.textBrowser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.textBrowser.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"frii-config", None))
        self.addButton.setText(QCoreApplication.translate("Form", u"Next", None))
        self.path.setText(QCoreApplication.translate("Form", u"Enter repository path here", None))
        self.remote.setText(QCoreApplication.translate("Form", u"Enter repository URL here", None))
        self.checkBox.setText(QCoreApplication.translate("Form", u"Clone repository", None))
        self.apply.setText(QCoreApplication.translate("Form", u"Save", None))
        self.delentry.setText(QCoreApplication.translate("Form", u"Delete", None))
        self.cancel.setText(QCoreApplication.translate("Form", u"Cancel", None))
        self.changeButton.setText(QCoreApplication.translate("Form", u"Change", None))
        self.configlabel.setText(QCoreApplication.translate("Form", u"Config path:", None))
    # retranslateUi

