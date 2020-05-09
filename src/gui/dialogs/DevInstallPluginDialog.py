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
from PyQt5.QtCore import QThread

from gui.dialogs.InstallPluginsDialog import InstallPluginsDialog, InstallThread
from utils import dev_install


class DevInstallPluginDialog(InstallPluginsDialog):
    def create_thread(self, plugin_handler, urls) -> QThread:
        return DevInstallThread(plugin_handler, urls)


class DevInstallThread(InstallThread):
    def run(self) -> None:
        for index, code in enumerate(self.to_install):
            self.progress_signal.emit(index, len(self.to_install), code)

            yaml_text = dev_install.get_plugin_yaml_text(code)

            if yaml_text:
                self.plugin_handler.dev_install_plugin(yaml_text)
            else:
                raise Exception("Could not get YAML text for plugin.")

        self.progress_signal.emit(len(self.to_install), len(self.to_install), None)
