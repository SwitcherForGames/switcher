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
from typing import List

from PyQt5.QtWidgets import QDialog
from send2trash.plat_other import uid

from utils import resources


class InstallFromGithubIDDialog(QDialog):
    def __init__(self, application, plugin_handler, ids: List[int]):
        super(InstallFromGithubIDDialog, self).__init__()

        self.ids = ids
        self.plugin_handler = plugin_handler
        self.application = application

        uid.loadUi(resources.get_github_install_dialog_layout())

        self.setWindowTitle("Install plugins")
