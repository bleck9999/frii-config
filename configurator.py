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
file_path = "../info.json"
# TODO:
# - check if entry exists (cli/gui)
# - edit entries
# - change config file path (gui)
# - option to delete folder as well as entry
# - allow cli arguments                           done


class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.urlregexp = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.ui.table.setHorizontalHeaderLabels(["Colour", "Path"])
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
    def apply(quiet=False):
        json.dump({"repos": repos,
                   "sysupdates": sysupdates}, open(file_path, "w"))
        if not quiet:
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
    def addRepoFromExisting(path, hexcolour, quiet=False):
        try:
            repo = git.Repo(path)
        except git.exc.NoSuchPathError:
            if quiet:
                print("Path not found")
            else:
                errbox = QMessageBox()
                errbox.setText("Path not found")
                errbox.exec()                               # look we've got error messages and everything
            return 1
        except git.exc.InvalidGitRepositoryError:       # means it *has* to be good code
            if quiet:
                print("Path does not contain a valid git repository")
            else:
                errbox = QMessageBox()
                errbox.setText("Path does not contain a valid git repository")
                errbox.exec()
            return 1
        if "origin" in repo.remotes:
            if not repo.remotes["origin"].url:
                if quiet:
                    print("Missing origin URL, how on earth did you manage that?")
                else:
                    errbox = QMessageBox()
                    errbox.setText("Missing origin URL, how on earth did you manage that?")
                    errbox.exec()  # if anyone manages to get this error i will be very surprised
                return 1
        else:
            if quiet:
                print("Repo has no origin")
            else:
                errbox = QMessageBox()
                errbox.setText("Repo has no origin")
                errbox.exec()
            return 1

        repos.append([path, int(hexcolour, 16)])

        if quiet:
            print(f"Successfully added repository at {path}!")
        else:
            msgbox = QMessageBox()
            msgbox.setText(f"Successfully added repository at {path}!")
            msgbox.exec()
        return

    @staticmethod
    def addNewRepo(path, remote, hexcolour, quiet=False):
        if os.path.exists(path):
            if os.path.isfile(path) or os.listdir(path):
                if quiet:
                    print("Path must be an empty directory")
                else:
                    errbox = QMessageBox()
                    errbox.setText("Path must be an empty directory")
                    errbox.exec()
                return 1
        else:
            if os.path.exists(path[:path.rindex('/')]):
                if quiet:
                    print("Specified folder does not exist but is in a valid directory.")
                    if input("Would you like to create the folder and clone the repository there? [Y/N]: ").lower().strip() != 'y':
                        print("Exiting.")
                        return 1
                    os.mkdir(path)
                else:
                    errbox = QMessageBox()
                    errbox.setText("Specified folder does not exist but is in a valid directory.\n"
                                   "Would you like to create the folder and clone the repository there?")
                    errbox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                    errbox.setDefaultButton(QMessageBox.Yes)
                    if errbox.exec() == QMessageBox.No:
                        return 1
                    os.mkdir(path)
            else:
                if quiet:
                    print("Path not found")
                else:
                    errbox = QMessageBox()
                    errbox.setText("Path not found")
                    errbox.exec()
                return 1

        os.system(f"git clone '{remote}' '{path}' -v")  # forget it im not dealing with gitpythons bs
        repos.append([path, int(hexcolour, 16)])

        if quiet:
            print(f"Repository successfully cloned to {path}")
        else:
            msgbox = QMessageBox()
            msgbox.setText(f"Repository successfully cloned to {path}")
            msgbox.exec()
        return


helptext = """
Usage:
configurator.py <arguments> <path> <colour>

Path:   Path where the repository will be cloned (if -c is specified) and added to the config
Colour: Colour code in hex (RRGGBB) used for embeds about the specified repository

Arguments:
-c url  / --clone=url           clone the repo at $url to $path
-d      / --delete              removes the repo at $path from the config file
-o file / --config-file=file    outputs to the config file at the specified path, rather than `../info.json`
-l      / --list                shows all entries currently in the specified config file
-h      / --help                shows help
"""
if __name__ == '__main__':
    if len(sys.argv) > 1:
        url = ''
        path = ''
        colour = ''
        mode = 'a'
        # argparse does not exist and i will not use it
        for opt in enumerate(sys.argv[1:]):
            if opt[1].startswith('-'):
                # switch statements in python when
                if opt[1] == "-c":
                    url = sys.argv[opt[0]+2]        # why +2?
                elif opt[1].startswith("--clone"):  # same reason as explained below
                    url = opt[1].split('=')[1]
                elif opt[1] == "-o":
                    file_path = sys.argv[opt[0]+2]
                elif opt[1].startswith("--config-file"):
                    file_path = opt[1].split('=')[1]
                elif opt[1] == '-d' or opt[1] == "--delete":
                    mode = 'd'
                elif opt[1] == '-l' or opt[1] == "--list":
                    mode = 'l'
                elif opt[1] == '-h' or opt[1] == "--help":
                    print(helptext)
                    sys.exit()
            else:
                # you might think that it should be sys.argv[opt[0]-1]
                # but opt[0] is the index for sys.argv[1:], not sys.argv
                # so opt[0]-1 would be 2 items before and would not only be wrong
                # but could also be out of bounds
                if sys.argv[opt[0]] != '-o' and sys.argv[opt[0]] != '-c':
                    if re.match("[0-9a-fA-F]{6,}", opt[1]):
                        colour = opt[1]
                    else:
                        path = opt[1]

        if len(sys.argv) < 3 and mode == 'a':
            print("No colour provided")
            sys.exit(2)
        if colour == '' and mode == 'a':
            print("Invalid colour provided")
            sys.exit(2)
        if os.path.exists(file_path):
            file = json.load(open(file_path))
            sysupdates = file["sysupdates"]
            repos = file["repos"]
        else:
            if input("Specified config file does not exist. Create it? [Y/N]: ").lower() == 'y':
                open(file_path, 'w')
            else:
                sys.exit()

        if mode == 'd':
            print("The following entry will be deleted: ")  # i might've let this accept multiple but i don't know how
            print(path)
            if input("Are you sure? [Y/N]: ").lower() == 'y':
                for repo in enumerate(repos):
                    if repo[1][0] == path:
                        repos.pop(repo[0])
                        break
                else:
                    print("Entry not found, no changes made")
                    sys.exit()
                print("Entry deleted, saving changes.")
                Form.apply(True)
            else:
                print("Exiting")
                sys.exit()
        elif mode == 'l':
            print(f"Entries in {file_path}")
            for i in repos:
                print(f"{i[0]}, {hex(i[1])}")
        elif mode == 'a':
            if url != '':
                if Form.addNewRepo(path, url, colour, True):
                    sys.exit(1)
            else:
                if Form.addRepoFromExisting(path, colour, True):
                    sys.exit(1)
            print("Saving changes")
            Form.apply(True)

    else:
        if os.path.exists(file_path):
            file = json.load(open(file_path))
            sysupdates = file["sysupdates"]
            repos = file["repos"]
        # Create the Qt Application
        app = QApplication()
        # Create and show the form
        form = Form()
        form.show()
        # Run the main Qt loop
        sys.exit(app.exec_())
