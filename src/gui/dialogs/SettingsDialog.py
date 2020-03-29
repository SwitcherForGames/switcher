#  Switcher, a tool for managing graphics and keymap profiles in games.
#  Copyright (C) 2020 Sam McCormack
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <https://www.gnu.org/licenses/>.
import os
import shutil
import time
from os.path import join
from uuid import uuid4

from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QFileDialog, QMessageBox

from api import files
from utils import resources, settings
from utils.settings import Settings


class MoveFolderThread(QThread):
    signal_done = pyqtSignal(bool, str)

    def __init__(self, old_location, new_location):
        super().__init__()

        self.old_location = old_location
        self.new_location = new_location

    def run(self):
        if self.new_location == self.old_location:
            return self.signal_done.emit(
                False,
                f"New directory is the same as the current directory: "
                f"{self.old_location}.",
            )

        if not self.has_write_permissions(self.new_location):
            return self.signal_done.emit(
                False, f"No write permissions for '{self.new_location}'."
            )

        try:
            shutil.copytree(self.old_location, self.new_location, dirs_exist_ok=True)
        except Exception as e:
            return self.signal_done.emit(False, str(e))

        try:
            # Handle when the directory is moved from the default location, which will still contain the logs/settings.
            if files._switcher_directory == self.old_location:
                # Delete the old folders, e.g. "plugins".
                for f in os.listdir(self.old_location):
                    filepath = join(self.old_location, f)
                    if os.path.isdir(filepath):
                        print(f"Deleting {filepath}...")
                        shutil.rmtree(filepath)

                # Delete the new log file, which isn't actually being used.
                os.remove(join(self.new_location, "switcher.log"))

            # Handle when the directory is changed from one non-default location to another.
            else:
                shutil.rmtree(self.old_location)
        except Exception as e:
            return self.signal_done.emit(True, str(e))

        time.sleep(1)
        return self.signal_done.emit(True, "")

    def has_write_permissions(self, folder: str) -> bool:
        os.makedirs(folder, exist_ok=True)

        tempfile = join(folder, f"{uuid4()}")
        try:
            file = open(tempfile, "w")
            file.close()

            os.remove(tempfile)
        except:
            return False

        return True


class SettingsDialog(QDialog):
    def __init__(self, *args):
        super().__init__(*args)

        self.prefs: Settings = settings.get_instance()
        self.can_close = True

        self.line_location: QLineEdit = None
        self.btn_location: QPushButton = None
        self.btn_ok: QPushButton = None

        uic.loadUi(resources.get_settings_layout(), self)

        self.line_location.setText(self.prefs.switcher_directory)
        self.btn_location.clicked.connect(self.on_change_location_clicked)
        self.btn_ok.clicked.connect(self.on_ok_clicked)

        self.set_move_in_progress(False)

        self.thread = None

    def set_move_in_progress(self, progress: bool) -> None:
        self.progress_location.setVisible(progress)
        self.btn_location.setVisible(not progress)
        self.btn_ok.setEnabled(not progress)

        self.can_close = not progress

    def on_move_complete(self, success: bool, error_msg: str = None) -> None:
        self.set_move_in_progress(False)

        if success:
            self.prefs.switcher_directory = self.line_location.text()
            self.prefs.commit()

        if error_msg:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText(error_msg)

            msg.exec()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Success")
            msg.setText("Switcher directory was moved successfully.")

            msg.exec()

        self.line_location.setText(self.prefs.switcher_directory)

    def on_change_location_clicked(self) -> None:
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.DirectoryOnly)

        if QDialog.Accepted == dialog.exec():
            new_location = dialog.selectedFiles()[0]

            if os.path.exists(new_location) and os.listdir(new_location):
                _, suffix = os.path.split(self.prefs.switcher_directory)
                new_location = join(new_location, suffix)

            self.line_location.setText(new_location)
            self.set_move_in_progress(True)

            self.thread = MoveFolderThread(self.prefs.switcher_directory, new_location)
            self.thread.signal_done.connect(self.on_move_complete)
            self.thread.start()

    def on_ok_clicked(self) -> None:
        if self.can_close:
            self.close()

    def closeEvent(self, e: QCloseEvent) -> None:
        if not self.can_close:
            e.ignore()
