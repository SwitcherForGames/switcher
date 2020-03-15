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
import subprocess

from PyQt5 import uic
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QDialog, QProgressBar, QLabel, QPushButton

from updates.UpdateHandler import UpdateHandler, DownloadThread
from utils import resources


class UpdateDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.progress_bar: QProgressBar = None
        self.lbl_status: QLabel = None
        self.btn_cancel: QPushButton = None
        self.btn_close: QPushButton = None

        uic.loadUi(resources.get_update_dialog_layout(), self)

        self.setWindowTitle("Install update")

        self.lbl_status.setText("Downloading update information...")
        self.btn_cancel.clicked.connect(self.on_cancel_clicked)

        self.btn_close.clicked.connect(self.on_close_clicked)
        self.btn_close.hide()

        self.progress_bar.setValue(0)
        self.progress_bar.setRange(0, 0)

        self.download_thread = DownloadThread()

        self.download_thread.signal_download_started.connect(
            lambda: self.progress_bar.setRange(0, 100)
        )
        self.download_thread.signal_download_progress.connect(self.on_download_progress)
        self.download_thread.signal_installer_name.connect(self.on_name_found)

        self.download_thread.signal_verify_started.connect(self.on_verify_started)
        self.download_thread.signal_verify_finished.connect(self.on_verify_finished)
        self.download_thread.signal_installer_path.connect(self.launch_installer)

        self.download_thread.start()

    def launch_installer(self, location: str):
        self.progress_bar.hide()
        subprocess.Popen([location, "/SILENT", "/RESTARTAPPLICATIONS"])

    def on_error(self):
        self.btn_cancel.hide()
        self.btn_close.show()

    def on_verify_started(self):
        self.lbl_status.setText(f"Verifying integrity of installer...")
        self.progress_bar.setRange(0, 0)

    def on_verify_finished(self, success: bool):
        if not success:
            self.lbl_status.setText(
                f"Error: checksums do not match. Downloaded installer is not genuine. "
                f"\n\nThis is probably caused by a download error. Please try again."
            )
            self.progress_bar.hide()
            return self.on_error()

        self.lbl_status.setText(
            f"Installer verified. Please accept the UAC dialog when it appears."
        )

    def on_name_found(self, name: str):
        self.lbl_status.setText(f"Downloading {name} from GitHub...")

    def on_download_progress(self, progress: float):
        self.progress_bar.setValue(progress * 100)

    def on_cancel_clicked(self):
        self.close()

    def on_close_clicked(self):
        self.close()

    def closeEvent(self, event: QCloseEvent):
        self.download_thread.terminate()
