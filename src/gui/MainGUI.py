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
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QListWidget,
    QPushButton,
    QGridLayout,
    QLabel,
    QCheckBox,
    QLineEdit,
    QProgressBar,
)


class MainGUI:
    def __init__(self):
        self.left: QVBoxLayout = None
        self.right: QVBoxLayout = None
        self.listwidget_plugins: QListWidget = None
        self.btn_plugins: QPushButton = None

        self.grid: QGridLayout = None
        self.listwidget_profiles: QListWidget = None

        self.btn_save_profile: QPushButton = None

        self.btn_browse: QPushButton = None
        self.lbl_game_loc: QLabel = None

        self.chk_game_saves: QCheckBox = None
        self.chk_graphics: QCheckBox = None
        self.chk_keymaps: QCheckBox = None

        self.btn_play: QPushButton = None

        self.edit_profile_name: QLineEdit = None
        self.lbl_update: QLabel = None

        self.progress_save_profile: QProgressBar = None

        self.btn_settings: QPushButton = None
        self.btn_autoinstall: QPushButton = None
