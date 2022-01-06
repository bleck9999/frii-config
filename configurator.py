import configparser
import sys
import re
import git
import json
import os
import inspect
from itertools import chain
from colorpicker import ColorPicker
from PySide6.QtWidgets import (QApplication, QMainWindow, QMessageBox,
                               QTableWidgetItem, QFileDialog, QDialog)
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QColor, QFont
from mainwindow import Ui_MainWindow
from addinidialog import Ui_Dialog


# TODO:
# info.json changes for watching
# adding/deleting sections (maybe?)
# should probably find a way to clear the selection after deletions (both ini and json)


class AddIniDialog(QDialog):
    def __init__(self, parent=None):
        super(AddIniDialog, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.retval = "Cancel"

        self.ui.buttonBox.clicked.connect(self.a)

    @Slot()
    def a(self, button):
        self.retval = button.text()
        self.close()

    def exec_(self):
        super(AddIniDialog, self).exec_()
        return self.retval, self.ui.key.text(), self.ui.val.text()


class Form(QMainWindow):
    def __init__(self, json_path, ini_path, parent=None):
        super(Form, self).__init__(parent)
        self.urlregexp = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.json_path = json_path
        self.ini_path = ini_path
        jscontents = {"repos": [], "sysupdates": []}
        if os.path.exists(json_path):
            jscontents = json.load(open(json_path))
        inicontents = {}
        if os.path.exists(ini_path):
            inicontents = configparser.ConfigParser()
            inicontents.read(ini_path)
        self.inicontents = inicontents.__dict__["_sections"]  # python is a great language
        self.indices = {}
        n = 1
        for x in self.inicontents:
            self.indices[x] = n
            n += len(self.inicontents[x]) + 1
        self.repos = jscontents["repos"]
        self.sysupdates = jscontents["sysupdates"]
        self.selected = {"json": [], "ini": []}
        self.ui.table.setHorizontalHeaderLabels(["Colour", "Path"])
        self.ui.initable.setHorizontalHeaderLabels(["Key", "Value"])

        self.ui.actionExit_2.triggered.connect(self.exit)
        self.ui.actionSave.triggered.connect(lambda: self.apply())
        self.ui.addButton.clicked.connect(self.addRepoHandler)
        self.ui.apply.clicked.connect(lambda: self.apply(False))
        self.ui.checkBox.stateChanged.connect(lambda: self.ui.remote.setEnabled(self.ui.checkBox.isChecked()))
        self.ui.delentry.clicked.connect(self.deleteEntry)
        self.ui.iniadd.clicked.connect(self.addIniKey)
        self.ui.iniapply.clicked.connect(lambda: self.apply(False))
        self.ui.inidel.clicked.connect(self.deleteEntryini)
        self.ui.inipath.setText(self.ini_path)
        self.ui.initable.itemChanged.connect(self.onEditini)
        self.ui.initable.itemSelectionChanged.connect(lambda: self.onSelectedTableItem("ini"))
        self.ui.openjson.triggered.connect(lambda: self.openhandler("json"))
        self.ui.openini.triggered.connect(lambda: self.openhandler("ini"))
        self.ui.table.itemChanged.connect(self.onEditjson)
        self.ui.table.itemSelectionChanged.connect(lambda: self.onSelectedTableItem("json"))
        self.ui.textBrowser.setText(self.json_path)

        self.updateTables()

    @Slot()
    def addIniKey(self):
        if len(self.selected["ini"]) > 1:
            errbox = QMessageBox()
            errbox.setText("What do you want from me how do am I meant to know where you want to insert the new key like this?")
            errbox.exec()
            return

        for section in reversed(self.indices):
            # [0]: first and in theory only item
            # [1]: row number
            # +1 : meddling off-by-one errors
            # >= : if a section header is selected, expected behaviour would be insert under that section
            if (self.selected["ini"][0][1] + 1) >= self.indices[section]:
                dialog = AddIniDialog(self)
                dialog.show()
                # "Cancel"/"Apply",  key.text(),  value.text()
                res = dialog.exec_()
                if res[0] == "Cancel":
                    return
                else:
                    key, val = res[1], res[2]
                    if not key:
                        errbox = QMessageBox()
                        errbox.setText("Key cannot be empty")
                        errbox.exec()
                        return
                    if not val:
                        errbox = QMessageBox()
                        errbox.setText("Value cannot be empty")
                        errbox.exec()
                        return
                    self.inicontents[section][key] = val
                    self.updateTables()
                    return
                break

    def checkAndSaveChanges(self):
        old, oldini = {}, {}
        if open(self.json_path).read() != '':
            old = json.load(open(self.json_path))
        else:
            old = {"repos": [], "sysupdates": []}

        if open(self.ini_path).read() != '':
            oldini = configparser.ConfigParser().read(self.ini_path)
        else:
            oldini = {}

        if (old["repos"] == self.repos and old["sysupdates"] == self.sysupdates) or \
                (oldini == self.inicontents):
            pass
        else:
            confirm = QMessageBox()
            confirm.setText("You have unsaved changes. Would you like to save them now?")
            confirm.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            ret = confirm.exec()
            if ret == QMessageBox.Cancel:
                return 1
            elif ret == QMessageBox.Yes:
                self.apply()

    @Slot()
    def exit(self):
        self.checkAndSaveChanges()
        self.close()

    @Slot()
    def onEditini(self, item):
        if "self.updateTables" in inspect.stack()[2].code_context[0]:  # come at me
            return
        elif item.column() == 0:
            secs = 3  # SEX?!?!?!?!?!?!!?!
            for section in reversed(self.indices):
                if (item.row()+1) > self.indices[section]:  # first occurrence of this must always break to avoid repeating itself
                    if item.text() in self.inicontents[section]:
                        pass  # no change
                    else:
                        # pad: no. of section headers + no. of entries in previous sections
                        pad = secs + (len(self.inicontents[list(self.indices)[0]]) if secs > 1 else 0) + \
                              (len(self.inicontents[list(self.indices)[1]]) if secs > 2 else 0)
                        # list is so they can be indexed by num
                        originalKey = list(self.inicontents[section].keys()) \
                            [item.row() - pad]
                        if not item.text():
                            errbox = QMessageBox()
                            errbox.setText("Key cannot be empty")
                            errbox.exec()
                            item.setText(originalKey)
                            return
                        self.inicontents[section][item.text()] = self.ui.initable.item(item.row(), 1).text()
                        self.inicontents[section].pop(originalKey)
                        # this action changes the order of the dict in most cases, so without updating the table
                        # the actual position of items can desync which leads to very buggy behaviour
                        self.updateTables()
                    break
                secs -= 1

        else:  # item is a value, which should in theory require less fuckery
            secs = 3
            for section in reversed(self.indices):
                if (item.row()+1) > self.indices[section]:
                    key = self.ui.initable.item(item.row(), 0).text()
                    originalVal = self.inicontents[section][key]
                    if item.text() == originalVal:
                        pass
                    else:
                        if not item.text():
                            errbox = QMessageBox()
                            errbox.setText("Value cannot be empty")
                            errbox.exec()
                            item.setText(originalVal)
                            return
                        # TODO store types of keys and enforce typechecking
                        self.inicontents[section][key] = item.text()
                        self.updateTables()
                    break
                secs -= 1

    @Slot()
    def onEditjson(self, item):
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
    def openhandler(self, mode):
        if mode == "json":
            self.changePathJson()
        elif mode == "ini":
            self.changePathIni()
        else:
            a = QMessageBox()  # error handling (tm)
            a.setText("what the fuck")
            a.exec()
        return

    def changePathIni(self):
        tmp = QFileDialog.getOpenFileName(self, "Open config", os.getcwd(), "INI files (*.ini)")[0]
        if tmp != '':
            if self.checkAndSaveChanges() == 1:
                return

            if open(tmp).read() != '':
                contents = configparser.ConfigParser().read(tmp).__dict__["_sections"]
                self.inicontents = contents
            else:
                self.inicontents = {}
            self.updateTables()
            self.ini_path = tmp
            self.ui.inipath.setText(self.ini_path)

    def changePathJson(self):
        tmp = QFileDialog.getOpenFileName(self, "Open config", os.getcwd(), "JSON files (*.json)")[0]
        if tmp != '':
            if self.checkAndSaveChanges() == 1:
                return

            if open(tmp).read() != '':
                contents = json.load(open(tmp))
                self.repos = contents["repos"]
                self.sysupdates = contents["sysupdates"]
            else:
                self.repos = []
                self.sysupdates = []
            self.updateTables()
            self.json_path = tmp
            self.ui.textBrowser.setText(self.json_path)

    @Slot()
    def deleteEntryini(self):
        for k in self.inicontents:
            if k in self.selected["ini"]:
                errbox = QMessageBox()
                errbox.setText("Section headers cannot be deleted.")
                errbox.exec()
                return
        confirm = QMessageBox()
        msg = "The following keys will be deleted:\n"
        for key in self.selected["ini"]:
            msg += key[0] + "\n"
        msg += "Are you sure?"
        confirm.setText(msg)
        confirm.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if confirm.exec() != QMessageBox.Yes:
            return

        for item in self.selected["ini"]:
            for section in reversed(self.indices):
                if (item[1]+1) > self.indices[section]:
                    self.inicontents[section].pop(item[0])
                    break

        msgbox = QMessageBox()
        msgbox.setText(f"Successfully removed {len(self.selected['ini'])} entries!")
        msgbox.exec()

        self.updateTables()

    @Slot()
    def deleteEntry(self):
        confirm = QMessageBox()
        msg = "The following entries will be deleted:\n"
        for path in self.selected["json"]:
            msg += path + "\n"
        msg += "Are you sure?"
        confirm.setText(msg)
        confirm.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if confirm.exec() != QMessageBox.Yes:
            return

        delfiles = False
        confirm = QMessageBox()
        confirm.setText(f"Would you like to delete the folder{'s' if len(self.selected['json']) > 1 else ''} on disk as well?")
        confirm.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if confirm.exec() == QMessageBox.Yes:
            delfiles = True

        todel = []
        for repo in enumerate(self.repos):
            if repo[1][0] in self.selected['json']:
                todel.append(repo[0])
        todel.reverse()
        for i in todel:
            self.repos.pop(i)
            if delfiles:
                os.rmdir(self.repos[i][0])

        msgbox = QMessageBox()
        msgbox.setText(f"Successfully removed {len(todel)} entries!")
        msgbox.exec()

        self.updateTables()

    def updateTables(self):
        self.ui.table.setRowCount(len(self.repos))  # redraw table to update for any changes
        for i, r in enumerate(self.repos):
            self.ui.table.setItem(i, 1, QTableWidgetItem(r[0]))
            colourcell = QTableWidgetItem(f"0x{str(hex(r[1]))[2:].zfill(6)}")
            colourcell.setBackground(QColor(r[1]))
            colourcell.setFlags(colourcell.flags() & ~Qt.ItemIsEditable)
            self.ui.table.setItem(i, 0, colourcell)

        # total objects in nested dict, length of all values + number of columns
        self.ui.initable.setRowCount(sum(len(v) for v in self.inicontents.values()) + len(self.inicontents))
        secfont = QFont()
        secfont.setFamily(u"Sans Serif")
        secfont.setBold(True)
        pos = 0
        for sec in self.inicontents:
            item = QTableWidgetItem(sec)
            item.setFont(secfont)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.ui.initable.setItem(pos, 0, item)
            item = QTableWidgetItem()                           # empty tile next to section header
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)    # done to prevent editing the blank space
            self.ui.initable.setItem(pos, 1, item)
            pos += 1
            for k, v in zip(self.inicontents[sec].keys(), self.inicontents[sec].values()):
                self.ui.initable.setItem(pos, 0, QTableWidgetItem(k))
                self.ui.initable.setItem(pos, 1, QTableWidgetItem(v))
                pos += 1

    @Slot()
    def onSelectedTableItem(self, mode):
        if mode == "json":
            self.selected["json"].clear()
            if len(self.ui.table.selectedItems()) >= 2:  # at least 1 row is selected
                self.ui.delentry.setEnabled(True)
                for item in self.ui.table.selectedItems():
                    if item.column() == 1:
                        self.selected["json"].append(item.text())
            else:
                self.ui.delentry.setEnabled(False)

        elif mode == "ini":
            self.selected["ini"].clear()
            if len(self.ui.initable.selectedItems()) >= 2:  # at least 1 row is selected
                self.ui.inidel.setEnabled(True)
                self.ui.iniadd.setEnabled(True)
                for item in self.ui.initable.selectedItems():
                    if item.column() == 0:                  # here we want keys not values
                        self.selected["ini"].append((item.text(), item.row()))  # we need the row number for later use
            else:
                self.ui.inidel.setEnabled(False)
                self.ui.iniadd.setEnabled(False)

        else:
            raise Exception("You did a fuck")

    @Slot()
    def apply(self, quiet=True):
        json.dump({"repos": self.repos,
                   "sysupdates": self.sysupdates}, open(self.json_path, "w"))

        ini = configparser.ConfigParser()
        ini.__dict__["_sections"] = self.inicontents
        ini.write(open(self.ini_path, "w"))

        if not quiet:
            msgbox = QMessageBox()
            msgbox.setText("Done!")
            msgbox.exec()
        return

    @Slot()
    def addRepoHandler(self):
        path = self.ui.path.text()
        for r in enumerate(self.repos):
            if r[1][0] == path:
                errbox = QMessageBox()
                errbox.setText(f"{path} is already listed in {self.json_path}")
                errbox.exec()
                return
        colour = ColorPicker().getColor()
        hexcolour = '%02x%02x%02x' % (int(colour[0]),  # this is actually so dumb
                                      int(colour[1]) if int(colour[0]) != 255 or not int(colour[1]) else int(
                                          colour[1]) + 1,
                                      int(colour[2]) if int(colour[0]) != 255 or not int(colour[2]) else int(
                                          colour[2]) + 1)
        if self.ui.checkBox.isChecked():
            if not re.match(self.urlregexp, self.ui.remote.text()):
                errbox = QMessageBox()
                errbox.setText("Invalid URL")
                errbox.exec()
                return
            self.addNewRepo(path, self.ui.remote.text(), hexcolour, self.repos)
        else:
            self.addRepoFromExisting(path, hexcolour, self.repos)

        self.updateTables()

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
                errbox.exec()  # look we've got error messages and everything
            return 1
        except git.exc.InvalidGitRepositoryError:  # means it *has* to be good code
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
                    if input(
                            "Would you like to create the folder and clone the repository there? [Y/N]: ").lower().strip() != 'y':
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


if __name__ == '__main__':
    json_path = "../info.json"
    ini_path = "../frii_update.ini"

    # Create the Qt Application
    app = QApplication()
    # Create and show the form
    form = Form(json_path, ini_path)
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec())
