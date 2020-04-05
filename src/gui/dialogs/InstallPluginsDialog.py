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
from typing import List

from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QDialog, QProgressBar, QLabel, QPushButton

from api.PluginHandler import PluginHandler
from utils import resources


class InstallPluginsDialog(QDialog):
    def __init__(self, application, plugin_handler, urls):
        super().__init__()
        self.application = application

        self.progress_bar: QProgressBar = None
        self.lbl_status: QLabel = None
        self.btn_cancel: QPushButton = None
        self.btn_close: QPushButton = None

        uic.loadUi(resources.get_update_dialog_layout(), self)

        self.setWindowTitle("Install update")

        self.lbl_status.setText("Installing plugins...")
        self.btn_cancel.clicked.connect(self.on_cancel_clicked)
        self.btn_close.clicked.connect(self.close)

        self.progress_bar.setValue(0)
        self.progress_bar.setRange(0, 0)
        self.finished = False

        self.install_thread = InstallThread(plugin_handler, urls)
        self.install_thread.progress_signal.connect(self.on_progress)
        self.install_thread.start()

    def on_progress(self, done, total, url: str):
        if done >= total:
            self.lbl_status.setText(
                "Finished installing plugins. Restart Switcher to continue."
            )
            self.btn_cancel.hide()

            self.finished = True
            return self.progress_bar.hide()

        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(done)

        name = url.split("/")[-1]
        self.lbl_status.setText(f"Installing plugin: {name}...")

    def on_cancel_clicked(self):
        self.close()

    def closeEvent(self, event: QCloseEvent):
        super(InstallPluginsDialog, self).closeEvent(event)
        if self.finished:
            self.application.restart()
        else:
            self.install_thread.terminate()


class InstallThread(QThread):
    progress_signal = pyqtSignal(int, int, str)

    def __init__(self, plugin_handler: PluginHandler, to_install: List[str]):
        super().__init__()

        self.plugin_handler = plugin_handler
        self.to_install = to_install

    def run(self) -> None:
        for index, url in enumerate(self.to_install):
            self.progress_signal.emit(index, len(self.to_install), url)
            self.plugin_handler.install_plugin(url)

        self.progress_signal.emit(len(self.to_install), len(self.to_install), None)
