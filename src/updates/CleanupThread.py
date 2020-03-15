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

from PyQt5.QtCore import QThread


class CleanupThread(QThread):
    def __init__(self, installer_path: str, current_version: str):
        super().__init__()
        self.installer_path = installer_path
        self.current_version = current_version

    def run(self) -> None:
        for folder in os.listdir(self.installer_path):
            if folder <= self.current_version:
                shutil.rmtree(os.path.join(self.installer_path, folder))
