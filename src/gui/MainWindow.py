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
import asyncio
from typing import List, Optional

from PyQt5 import uic
from PyQt5.QtWidgets import (
    QMainWindow,
    QDialog,
    QFileDialog,
    QListWidget,
    QListWidgetItem,
)

from api.Launcher import Launcher
from api.Plugin import Plugin
from api.PluginHandler import PluginHandler
from api.profiles import ProfileType, Feature, SingleFeature, ComboFeature, Profile
from gui.MainGUI import MainGUI
from gui.ManagePluginsDialog import ManagePluginsDialog
from gui.PluginWidget import PluginWidget
from gui.ProfileWidget import ProfileWidget
from utils import resources


class MainWindow(MainGUI, QMainWindow):
    """
    The main window of the application.
    """

    def __init__(self, application):
        MainGUI.__init__(self)
        QMainWindow.__init__(self)

        self.plugin_widgets: List[PluginWidget] = []

        self.application = application
        self.plugin_handler: PluginHandler = application.plugin_handler

        self.plugin_handler.initialise()
        self.setup_ui()

    def setup_ui(self) -> None:
        uic.loadUi(resources.get_layout(), self)

        self.btn_plugins.clicked.connect(self.manage_plugins)
        self.btn_browse.clicked.connect(self.browse_for_game)

        self.btn_save_profile.clicked.connect(self.save_profile)

        self.btn_play.clicked.connect(self.on_play_clicked)

        plugins = self.plugin_handler.plugins

        cols = max(2, round(len(plugins) / 3))
        row, col = 0, 0

        for p in plugins:
            if col == cols:
                row += 1
                col = 0

            col += 1
            w = PluginWidget(p, self)
            self.grid.addWidget(w, row, col)

            self.plugin_widgets.append(w)
            asyncio.ensure_future(w.coro_initialise())

        if self.plugin_widgets:
            self.plugin_widgets[0].toggle_activation()

    def manage_plugins(self) -> None:
        dialog = ManagePluginsDialog(
            self, self.plugin_handler.get_installed_plugin_urls()
        )

        if dialog.exec() == QDialog.Accepted and (changes := dialog.get_changes()):
            self.plugin_handler.apply_changes(changes)
            self.application.restart()

    def on_plugin_activation_changed(self, plugin: Plugin) -> None:
        for p in self.plugin_widgets:
            if p.plugin is not plugin and p.active:
                p.toggle_activation(trigger=False)

        loc = plugin.game_path or "Game location unknown"
        self.lbl_game_loc.setText(loc)

        features = plugin.get_features()
        self._setup_check_boxes(features)
        self._update_profiles_list(plugin)

    def on_play_clicked(self) -> None:
        self.get_active_plugin().launch_game(Launcher.STEAM)

    def save_profile(self) -> None:
        plugin = self.get_active_plugin()

        feature = self.get_current_feature()
        name = self.edit_profile_name.text()

        profile = Profile.create(name, feature)
        self.plugin_handler.save_profile(plugin, profile)

        self._update_profiles_list(plugin)

    def apply_profile(self, profile: Profile) -> None:
        plugin = self.get_active_plugin()

        self.plugin_handler.apply_profile(plugin, profile)

    def delete_profile(self, profile: Profile) -> None:
        plugin = self.get_active_plugin()

        self.plugin_handler.delete_profile(plugin, profile)
        self._update_profiles_list(plugin)

    def _update_profiles_list(self, plugin: Plugin) -> None:
        list_widget: QListWidget = self.listwidget_profiles
        list_widget.clear()

        if profiles := sorted(
            self.plugin_handler.get_profiles(plugin), key=lambda i: i.time, reverse=True
        ):
            for p in profiles:
                w = ProfileWidget(p, plugin, self.plugin_handler, self)

                item = QListWidgetItem()
                item.setSizeHint(w.sizeHint())
                list_widget.addItem(item)
                list_widget.setItemWidget(item, w)

    def _setup_check_boxes(self, features: List[ProfileType]) -> None:
        for c in (self.chk_game_saves, self.chk_keymaps, self.chk_graphics):
            c.setChecked(False)
            c.setEnabled(False)

        for f in features:
            if f is ProfileType.GRAPHICS:
                self.chk_graphics.setChecked(True)
                self.chk_graphics.setEnabled(True)
            elif f is ProfileType.KEYMAPS:
                self.chk_keymaps.setChecked(True)
                self.chk_keymaps.setEnabled(True)
            elif f is ProfileType.GAME_SAVES:
                # Game saves are usually not a priority; don't enable by default.
                self.chk_game_saves.setChecked(False)
                self.chk_game_saves.setEnabled(True)

    def get_current_feature(self) -> Optional[Feature]:
        graphics = not self.chk_graphics.isChecked() or ProfileType.GRAPHICS
        keymaps = not self.chk_keymaps.isChecked() or ProfileType.KEYMAPS
        saves = not self.chk_game_saves.isChecked() or ProfileType.GAME_SAVES

        enabled: List = list(
            filter(lambda f: isinstance(f, ProfileType), (graphics, keymaps, saves))
        )

        if not enabled:
            return None
        elif len(enabled) == 1:
            return SingleFeature(enabled[0])
        else:
            return ComboFeature(*enabled)

    def browse_for_game(self) -> None:
        loc = QFileDialog.getExistingDirectory(
            self, "Open game folder", options=QFileDialog.ShowDirsOnly
        )

        p = self.get_active_plugin()

        if p.verify(loc):
            self.plugin_handler.save_game_path(loc, p)
            self.lbl_game_loc.setText(loc)

        return loc

    def get_active_plugin(self) -> Plugin:
        return self.get_active_plugin_widget().plugin

    def get_active_plugin_widget(self) -> PluginWidget:
        for w in self.plugin_widgets:
            if w.active:
                return w

    def resize_plugin_widgets(self):
        window_height = self.height()
        count = max(5, len(self.plugin_widgets))

        widget_height = window_height / count

        cap = 250
        if widget_height > cap:
            widget_height = cap

        for w in self.plugin_widgets:
            _width, _height = w.exact_size

            aspect_ratio = _width / _height
            widget_width = widget_height * aspect_ratio

            w.setFixedHeight(widget_height)
            w.setFixedWidth(widget_width)

            w.exact_size = (widget_width, widget_height)
            asyncio.ensure_future(w.coro_initialise())

            self.btn_plugins.setFixedWidth(widget_width)
