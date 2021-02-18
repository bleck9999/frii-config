import sys
import re
import git
import json
import os
from colorpicker import ColorPicker
from PySide6.QtWidgets import (QLineEdit, QPushButton, QApplication,
                               QVBoxLayout, QDialog, QMessageBox,
                               QCheckBox, QTableWidget, QTableWidgetItem)
from PySide6.QtCore import Slot
from PySide6.QtGui import QColor
from window import Ui_Form

repos = []
sysupdates = []
selected = []
# TODO:
# - load existing config                          done
# - create empty config if none is present        done
# - add repo from url, specify path to clone it   done
# - add existing repo, check origin url is valid  done
# - write changes to config                       done
# - colour picker                                 done
# - deal with the sysupdates part somehow         done
# - remove repositories                           done
# - allow cli arguments (maybe)
class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.urlregexp = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.addButton.clicked.connect(self.addHandler)
        self.ui.checkBox.stateChanged.connect(lambda: self.ui.remote.setEnabled(self.ui.checkBox.isChecked()))
        self.ui.apply.clicked.connect(self.apply)
        self.ui.table.itemSelectionChanged.connect(self.onSelectedTableItem)
        self.ui.cancel.clicked.connect(lambda: self.close())
        self.ui.delentry.clicked.connect(self.deleteEntry)

        self.updateTable()

    @Slot()
    def deleteEntry(self):
        confirm = QMessageBox()
        msg = "The following entries will be deleted:\n"
        for path in selected:
            msg += path + "\n"
        msg += "Are you sure?"
        confirm.setText(msg)
        confirm.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if confirm.exec() != QMessageBox.Yes:
            return

        todel = []
        for repo in enumerate(repos):
            if repo[1][0] in selected:
                todel.append(repo[0])
        todel.reverse()
        for i in todel:
            repos.pop(i)

        msgbox = QMessageBox()
        msgbox.setText(f"Successfully removed {len(todel)} entries!")
        msgbox.exec()

        self.updateTable()

    def updateTable(self):
        self.ui.table.setRowCount(len(repos))  # redraw table to update for any changes
        for i, r in enumerate(repos):
            self.ui.table.setItem(i, 1, QTableWidgetItem(r[0]))
            colourcell = QTableWidgetItem(f"0x{str(hex(r[1]))[2:].zfill(6)}")
            colourcell.setBackground(QColor(r[1]))
            self.ui.table.setItem(i, 0, colourcell)

    @Slot()
    def onSelectedTableItem(self):
        selected.clear()
        if len(self.ui.table.selectedItems()) >= 2:  # at least 1 row is selected
            self.ui.delentry.setEnabled(True)
            for item in self.ui.table.selectedItems():
                if item.column() == 1:
                    selected.append(item.text())
        else:
            self.ui.delentry.setEnabled(False)

    @staticmethod
    @Slot()
    def apply():
        json.dump({"repos": repos,
                   "sysupdates": sysupdates}, open("../info.json", "w"))
        msgbox = QMessageBox()
        msgbox.setText("Done!")
        msgbox.exec()
        return

    @Slot()
    def addHandler(self):
        path = self.ui.path.text()
        colour = ColorPicker().getColor()
        hexcolour = '%02x%02x%02x' % (int(colour[0]),  # this is actually so dumb
                                      int(colour[1]) if int(colour[0]) != 255 or not int(colour[1]) else int(colour[1]) + 1,
                                      int(colour[2]) if int(colour[0]) != 255 or not int(colour[2]) else int(colour[2]) + 1)
        if self.ui.checkBox.isChecked():
            if not re.match(self.urlregexp, self.ui.remote.text()):
                errbox = QMessageBox()
                errbox.setText("Invalid URL")
                errbox.exec()
                return
            self.addNewRepo(path, self.ui.remote.text(), hexcolour)
        else:
            self.addRepoFromExisting(path, hexcolour)

        self.updateTable()

    @staticmethod
    def addRepoFromExisting(path, hexcolour):
        try:
            repo = git.Repo(path)
        except git.exc.NoSuchPathError:
            errbox = QMessageBox()
            errbox.setText("Path not found")
            errbox.exec()                               # look we've got error messages and everything
            return
        except git.exc.InvalidGitRepositoryError:       # means it *has* to be good code
            errbox = QMessageBox()
            errbox.setText("Path does not contain a valid git repository")
            errbox.exec()
            return
        if "origin" in repo.remotes:
            if not repo.remotes["origin"].url:
                errbox = QMessageBox()
                errbox.setText("Missing origin URL, how on earth did you manage that?")
                errbox.exec()  # if anyone manages to get this error i will be very surprised
                return
        else:
            errbox = QMessageBox()
            errbox.setText("Repo has no origin")
            errbox.exec()
            return

        repos.append([path, int(hexcolour, 16)])

        msgbox = QMessageBox()
        msgbox.setText(f"Successfully added repository at {path}!")
        msgbox.exec()
        return

    @staticmethod
    def addNewRepo(path, remote, hexcolour):
        if os.path.exists(path):
            if os.path.isfile(path) or os.listdir(path):
                errbox = QMessageBox()
                errbox.setText("Path must be an empty directory")
                errbox.exec()
                return
        else:
            if os.path.exists(path[:path.rindex('/')]):
                errbox = QMessageBox()
                errbox.setText("Specified folder does not exist but is in a valid directory.\n"
                               "Would you like to create the folder and clone the repository there?")
                errbox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                errbox.setDefaultButton(QMessageBox.Yes)
                if errbox.exec() == QMessageBox.No:
                    return
                os.mkdir(path)
            else:
                errbox = QMessageBox()
                errbox.setText("Path not found")
                errbox.exec()
                return

        os.system(f"git clone {remote} {path} -v")  # forget it im not dealing with gitpythons bs

        msgbox = QMessageBox()
        msgbox.setText(f"Repository successfully cloned to {path}")
        msgbox.exec()
        return


if __name__ == '__main__':
    if os.path.exists("../info.json"):
        file = json.load(open("../info.json"))
        sysupdates = file["sysupdates"]
        repos = file["repos"]
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    form = Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
