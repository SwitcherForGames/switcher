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
from datetime import datetime

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget

from api.Plugin import Plugin
from api.PluginHandler import PluginHandler
from api.profiles import Profile
from utils import resources


class ProfileWidget(QWidget):
    def __init__(
        self, profile: Profile, plugin: Plugin, plugin_handler: PluginHandler, window
    ):
        super(ProfileWidget, self).__init__()

        from gui.MainWindow import MainWindow

        self.profile = profile
        self.plugin = plugin
        self.plugin_handler = plugin_handler
        self.window: MainWindow = window

        uic.loadUi(resources.get_profile_item_layout(), self)

        self.lbl_name.setText(profile.name)
        self.lbl_features.setText(", ".join(profile.feature.to_strings()))
        self.lbl_time.setText(
            datetime.utcfromtimestamp(profile.time).strftime("%Y-%m-%d %H:%M")
        )

        self.btn_edit.clicked.connect(self.on_edit_clicked)
        self.btn_apply.clicked.connect(self.on_apply_clicked)

    def on_apply_clicked(self) -> None:
        self.window.apply_profile(self.profile)

    def on_edit_clicked(self) -> None:
        self.window.delete_profile(self.profile)
