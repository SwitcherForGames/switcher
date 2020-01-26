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
import importlib
import os
from typing import Optional

from src.api.Platform import Platform
from src.api.Plugin import Plugin


class PluginHandler:
    plugins_folder = "plugins"

    def __init__(self):
        self.plugins = []
        self.import_plugins_folder()

        for folder in os.listdir(self.plugins_folder):
            module = self.import_plugin_module(folder)
            if module:
                plugin = module.plugin(Platform.get())
                self.plugins.append(plugin)

    def import_plugins_folder(self):
        importlib.import_module(self.plugins_folder)

    def import_plugin_module(self, folder: str) -> Optional[Plugin]:
        module_name = f"{self.plugins_folder}.{folder}.init"
        try:
            imported = importlib.import_module(module_name, package=self.plugins_folder)
            print(f"Imported plugin: {module_name}")
            return imported
        except Exception as e:
            print(e)
