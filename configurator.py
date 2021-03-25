import sys
import re
import git
import json
import os
from itertools import chain
from colorpicker import ColorPicker
from PySide6.QtWidgets import (QApplication, QDialog, QMessageBox,
                               QTableWidgetItem, QFileDialog)
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QColor
from window import Ui_Form
# TODO:
# nothing :D


class Form(QDialog):
    def __init__(self, contents, config_path, parent=None):
        super(Form, self).__init__(parent)
        self.urlregexp = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.config_path = config_path
        self.repos = contents["repos"]
        self.sysupdates = contents["sysupdates"]
        self.selected = []
        self.ui.table.setHorizontalHeaderLabels(["Colour", "Path"])

        self.ui.addButton.clicked.connect(self.addHandler)
        self.ui.apply.clicked.connect(lambda: self.apply([self.repos, self.sysupdates]))
        self.ui.cancel.clicked.connect(lambda: self.close())
        self.ui.changeButton.clicked.connect(self.changePath)
        self.ui.checkBox.stateChanged.connect(lambda: self.ui.remote.setEnabled(self.ui.checkBox.isChecked()))
        self.ui.delentry.clicked.connect(self.deleteEntry)
        self.ui.table.itemChanged.connect(self.onEdit)
        self.ui.table.itemSelectionChanged.connect(self.onSelectedTableItem)
        self.ui.textBrowser.setText(self.config_path)

        self.updateTable()

    @Slot()
    def onEdit(self, item):
        if item.text() in chain.from_iterable(self.repos) or self.isColour(item.text()):
            return  # no change
        else:
            if not item.text():
                errbox = QMessageBox()
                errbox.setText("Path cannot be empty")
                errbox.exec()
                item.setText(self.repos[item.row()][0])
                return
            try:
                git.Repo(item.text())
            except git.exc.NoSuchPathError:
                errbox = QMessageBox()
                errbox.setText("Path not found")
                errbox.exec()
                item.setText(self.repos[item.row()][0])
                return
            except git.exc.InvalidGitRepositoryError:
                errbox = QMessageBox()
                errbox.setText("Path does not contain a valid git repository")
                errbox.exec()
                item.setText(self.repos[item.row()][0])
                return
            else:
                self.repos[item.row()][0] = item.text()

    @Slot()
    def changePath(self):
        tmp = QFileDialog.getOpenFileName(self, "Open config", os.getcwd(), "JSON files (*.json)")[0]
        if tmp != '':
            if open(self.config_path).read() != '':
                old = json.load(open(self.config_path))
            else:
                old = {"repos": [], "sysupdates": []}

            if old["repos"] == self.repos and old["sysupdates"] == self.sysupdates:
                pass
            else:
                confirm = QMessageBox()
                confirm.setText("You have unsaved changes. Would you like to save them now?")
                confirm.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                ret = confirm.exec()
                if ret == QMessageBox.Cancel:
                    return
                elif ret == QMessageBox.Yes:
                    self.apply([self.repos, self.sysupdates])

            if open(tmp).read() != '':
                contents = json.load(open(tmp))
                self.repos = contents["repos"]
                self.sysupdates = contents["sysupdates"]
            else:
                self.repos = []
                self.sysupdates = []
            self.updateTable()
            self.config_path = tmp
            self.ui.textBrowser.setText(self.config_path)

    @Slot()
    def deleteEntry(self):
        confirm = QMessageBox()
        msg = "The following entries will be deleted:\n"
        for path in self.selected:
            msg += path + "\n"
        msg += "Are you sure?"
        confirm.setText(msg)
        confirm.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if confirm.exec() != QMessageBox.Yes:
            return

        delfiles = False
        confirm = QMessageBox()
        confirm.setText(f"Would you like to delete the folder{'s' if len(self.selected) > 1 else ''} on disk as well?")
        confirm.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if confirm.exec() != QMessageBox.Yes:
            delfiles = True

        todel = []
        for repo in enumerate(self.repos):
            if repo[1][0] in self.selected:
                todel.append(repo[0])
        todel.reverse()
        for i in todel:
            self.repos.pop(i)
            if delfiles:
                os.rmdir(i)

        msgbox = QMessageBox()
        msgbox.setText(f"Successfully removed {len(todel)} entries!")
        msgbox.exec()

        self.updateTable()

    def updateTable(self):
        self.ui.table.setRowCount(len(self.repos))  # redraw table to update for any changes
        for i, r in enumerate(self.repos):
            self.ui.table.setItem(i, 1, QTableWidgetItem(r[0]))
            colourcell = QTableWidgetItem(f"0x{str(hex(r[1]))[2:].zfill(6)}")
            colourcell.setBackground(QColor(r[1]))
            colourcell.setFlags(colourcell.flags() & ~Qt.ItemIsEditable)
            self.ui.table.setItem(i, 0, colourcell)

    @Slot()
    def onSelectedTableItem(self):
        self.selected.clear()
        if len(self.ui.table.selectedItems()) >= 2:  # at least 1 row is selected
            self.ui.delentry.setEnabled(True)
            for item in self.ui.table.selectedItems():
                if item.column() == 1:
                    self.selected.append(item.text())
        else:
            self.ui.delentry.setEnabled(False)

    @staticmethod
    @Slot()
    def apply(contents, quiet=False):
        json.dump({"repos": contents[0],
                   "sysupdates": contents[1]}, open(config_path, "w"))
        if not quiet:
            msgbox = QMessageBox()
            msgbox.setText("Done!")
            msgbox.exec()
        return

    @Slot()
    def addHandler(self):
        path = self.ui.path.text()
        for r in enumerate(repos):
            if r[1][0] == path:
                errbox = QMessageBox()
                errbox.setText(f"{path} is already listed in {config_path}")
                errbox.exec()
                return
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
            self.addNewRepo(path, self.ui.remote.text(), hexcolour, self.repos)
        else:
            self.addRepoFromExisting(path, hexcolour, self.repos)

        self.updateTable()

    @staticmethod
    def addRepoFromExisting(path, hexcolour, repos, quiet=False):
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
        except git.exc.InvalidGitRepositoryError:           # means it *has* to be good code
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
    def addNewRepo(path, remote, hexcolour, repos, quiet=False):
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

    def isColour(self, col: str):
        for x in self.repos:
            if f"0x{str(hex(x[1]))[2:].zfill(6)}" == col:
                return True
        return False


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
    repos = []
    sysupdates = []
    config_path = "../info.json"

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
                    config_path = sys.argv[opt[0] + 2]
                elif opt[1].startswith("--config-file"):
                    config_path = opt[1].split('=')[1]
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
        if os.path.exists(config_path):
            file = json.load(open(config_path))
            sysupdates = file["sysupdates"]
            repos = file["repos"]
        else:
            if input("Specified config file does not exist. Create it? [Y/N]: ").lower() == 'y':
                open(config_path, 'w')
            else:
                sys.exit()

        if mode == 'd':
            print("The following entry will be deleted: ")  # i might've let this accept multiple but i don't know how
            print(path)
            if input("Are you sure? [Y/N]: ").lower() == 'y':
                for repo in enumerate(repos):
                    if repo[1][0] == path:
                        repos.pop(repo[0])
                        if input("Would you like to on disk as well? [Y/N]: ").lower() == 'y':
                            os.rmdir(path)
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
            print(f"Entries in {config_path}")
            for i in repos:
                print(f"{i[0]}, {hex(i[1])}")
        elif mode == 'a':
            for r in enumerate(repos):
                if r[1][0] == path:
                    print(f"{path} is already listed in {config_path}")
                    sys.exit(1)
            if url != '':
                if re.match("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", url):
                    if Form.addNewRepo(path, url, colour, repos, True):
                        sys.exit(1)
                else:
                    print("Invalid url provided")
                    sys.exit(2)
            else:
                if Form.addRepoFromExisting(path, colour, repos, True):
                    sys.exit(1)
            print("Saving changes")
            Form.apply([repos, sysupdates], True)

    else:
        file = []
        if os.path.exists(config_path):
            file = json.load(open(config_path))
        # Create the Qt Application
        app = QApplication()
        # Create and show the form
        form = Form(file, config_path)
        form.show()
        # Run the main Qt loop
        sys.exit(app.exec_())
