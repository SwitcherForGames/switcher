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
import logging
import webbrowser
from typing import List, Optional

from PyQt5 import uic, QtGui
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPixmap, QPalette, QBrush
from PyQt5.QtWidgets import (
    QMainWindow,
    QDialog,
    QFileDialog,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QMessageBox,
    QGraphicsBlurEffect,
)
from github.GitRelease import GitRelease

from api import GameFinder
from api.Launcher import Launcher
from api.Plugin import Plugin
from api.PluginHandler import PluginHandler
from api.profiles import ProfileType, Feature, SingleFeature, ComboFeature, Profile
from gui.MainGUI import MainGUI
from gui.dialogs.InstallPluginsDialog import InstallPluginsDialog
from gui.dialogs.ManagePluginsDialog import ManagePluginsDialog
from gui.dialogs.SettingsDialog import SettingsDialog
from gui.dialogs.UpdateDialog import UpdateDialog
from gui.widgets.PluginWidget import PluginWidget
from gui.widgets.ProfileWidget import ProfileWidget
from updates.UpdateHandler import UpdateHandler
from updates.UpdateStatus import UpdateStatus
from utils import resources, settings, errorhandling


class MainWindow(MainGUI, QMainWindow):
    """
    The main window of the application.
    """

    def __init__(self, application, *args):
        MainGUI.__init__(self)
        QMainWindow.__init__(self, *args)

        errorhandling.add_hook(self.except_hook)
        self.prefs = settings.get_instance()

        self.plugin_widgets: List[PluginWidget] = []

        self.application = application
        self.plugin_handler: PluginHandler = application.plugin_handler

        self.game_finder = GameFinder.get()
        self.effect = QGraphicsBlurEffect()

        self.update_handler: UpdateHandler = UpdateHandler()
        self.update_status = UpdateStatus.UNKNOWN

        self.plugin_handler.initialise()
        self.setup_ui()

        asyncio.ensure_future(self.check_for_updates())
        asyncio.ensure_future(self.coro_find_games())

    def setup_ui(self) -> None:
        uic.loadUi(resources.get_layout(), self)

        self.progress_save_profile.hide()
        self.progress_save_profile.setRange(0, 0)

        self.btn_plugins.clicked.connect(self.manage_plugins)
        self.btn_browse.clicked.connect(self.browse_for_game)

        self.btn_save_profile.clicked.connect(self.save_profile)
        self.btn_settings.clicked.connect(self.open_settings)

        self.btn_play.clicked.connect(self.on_play_clicked)
        self.btn_autoinstall.clicked.connect(self.autoinstall_plugins)

        self.lbl_update = QLabel()
        self.lbl_update.mousePressEvent = self.on_update_lbl_clicked
        self.lbl_update.setMargin(8)
        self.statusBar().addPermanentWidget(self.lbl_update)

        self.refresh_update_lbl()

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

    async def check_for_updates(self, force=False):
        if force or self.update_handler.should_check_for_updates():
            self.update_status = UpdateStatus.CHECKING
            self.refresh_update_lbl()

            new_release: GitRelease = await self.update_handler.get_latest_version()

            if new_release.tag_name > self.update_handler.get_current_version():
                new_tag = new_release.tag_name
                logging.info(f"New version available: {new_tag}")
                self.update_status = UpdateStatus.UPDATE_AVAILABLE
                self.refresh_update_lbl(version=new_tag)

                self.prefs.new_release_tag = new_tag
                self.prefs.commit()
            else:
                self.update_status = UpdateStatus.NO_UPDATES_AVAILABLE
                self.refresh_update_lbl()
                self.update_handler.cleanup()

        elif new_tag := self.prefs.new_release_tag:
            if new_tag > self.update_handler.get_current_version():
                self.update_status = UpdateStatus.UPDATE_AVAILABLE
                self.refresh_update_lbl(version=new_tag)
            else:
                self.prefs.new_release_tag = None
                self.prefs.commit()
                self.update_handler.cleanup()

    def autoinstall_plugins(self) -> None:
        asyncio.ensure_future(self.coro_find_games(force=True))

    async def coro_find_games(self, force=False):
        games = await self.game_finder.coro_find_games()

        cache = self.prefs.games
        unique = [loc for loc, _ in games.items() if loc not in cache]

        if unique or force:
            logging.info(f"Found unique games: {games.values()}")
            self.prefs.games = list(games.keys())
            self.prefs.commit()

            to_install = await self.plugin_handler.suggest_plugins(games)
            if to_install:
                InstallPluginsDialog(
                    self.application, self.plugin_handler, to_install
                ).exec()
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText(
                    "Could not discover any new plugins for installed games.\n\n"
                    'Try using "Manage plugins" to look for community plugins and list all available plugins.'
                )
                msg.setWindowTitle("No plugins found")
                msg.exec()
        else:
            print(f"No unique games found.")

    def refresh_update_lbl(self, version=None):
        if version:
            text = f"Click to update to {version}"
        else:
            text = self.update_status.value

        if self.update_status is not UpdateStatus.NO_UPDATES_AVAILABLE:
            self.lbl_update.setStyleSheet("text-decoration: underline; color: blue")
        else:
            self.lbl_update.setStyleSheet("color: black")

        self.lbl_update.setText(text)

    def on_update_lbl_clicked(self, event):
        if self.update_status is UpdateStatus.UPDATE_AVAILABLE:
            self.start_update()
        elif self.update_status is UpdateStatus.UNKNOWN:
            asyncio.ensure_future(self.check_for_updates(True))

    def start_update(self) -> None:
        UpdateDialog().exec()

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

        asyncio.ensure_future(self._update_background(plugin))

    def on_play_clicked(self) -> None:
        self.get_active_plugin().launch_game(Launcher.STEAM)

    def save_profile(self) -> None:
        self.update_save_progress(True)

        plugin = self.get_active_plugin()

        feature = self.get_current_feature()
        name = self.edit_profile_name.text()

        profile = Profile.create(name, feature)

        try:
            self.plugin_handler.save_profile(plugin, profile)
        except Exception as e:
            self.plugin_handler.delete_profile(plugin, profile)
            self.update_save_progress(False)
            raise e

        dialog = QMessageBox()
        dialog.setText(f"Created profile: '{profile.name}'.")
        dialog.setWindowTitle("Created profile")
        dialog.exec()

        self._update_profiles_list(plugin)
        self.update_save_progress(False)

    def update_save_progress(self, in_progress: bool) -> None:
        self.progress_save_profile.setVisible(in_progress)
        self.btn_save_profile.setVisible(not in_progress)

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

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        asyncio.ensure_future(self._update_background(self.get_active_plugin()))

    def open_settings(self) -> None:
        dialog = SettingsDialog()
        dialog.exec()

    def except_hook(self, type, value, traceback) -> None:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(f"Error ({type.__name__}):\n\n{value}")
        msg.setWindowTitle("Error")

        msg.addButton("Dismiss", QMessageBox.YesRole)
        msg.addButton("Report bug", QMessageBox.HelpRole)

        if QMessageBox.Accepted == msg.exec():
            webbrowser.open_new_tab(
                "https://github.com/SwitcherForGames/switcher/issues/new"
            )

    def closeEvent(self, *args, **kwargs) -> None:
        errorhandling.remove_hook(self.except_hook)

    async def _update_background(self, plugin: Plugin) -> None:
        backgrnd = QPixmap(await plugin.get_library_hero())
        aspect_ratio = backgrnd.width() / backgrnd.height()

        rect = self.size()
        # rect.setWidth(rect.width() * aspect_ratio)
        rect.setHeight(rect.height() * aspect_ratio)

        xmargin = (rect.width() - backgrnd.width()) / aspect_ratio / 2
        backgrnd = backgrnd.copy(
            QRect(xmargin, 0, rect.width() - xmargin, rect.height())
        )

        backgrnd = backgrnd.scaled(
            self.size(), Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation
        )

        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(backgrnd))
        self.setPalette(palette)

        # self.effect.setBlurRadius(10)
        # self.setGraphicsEffect(self.effect)
