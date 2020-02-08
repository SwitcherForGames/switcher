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
import logging
import os
from os.path import join
from typing import Optional, List

from api.CodelessPlugin import CodelessPlugin
from src.api.Platform import Platform
from src.api.Plugin import Plugin


class PluginHandler:
    """
    Class which handles importing plugins.
    """

    plugins_folder = "plugins"

    def __init__(self):
        self.plugins: List[Plugin] = []

    def initialise(self) -> None:
        self.import_plugins_folder()

        for folder in os.listdir(self.plugins_folder):
            if "init.py" in os.listdir(join(self.plugins_folder, folder)):
                module = self.import_plugin_module(folder)
                if module:
                    print(f"Loading normal plugin: {folder}")
                    plugin: Plugin = module.plugin(Platform.get())
            else:
                print(f"Loading codeless plugin: {folder}")
                plugin: Plugin = CodelessPlugin(
                    Platform.get(), join(self.plugins_folder, folder)
                )

            if plugin:
                self.plugins.append(plugin)

    def import_plugins_folder(self) -> None:
        """
        Imports the plguins folder. This must be done before importing any plugins in subfolders.
        """
        importlib.import_module(self.plugins_folder)

    def import_plugin_module(self, folder: str) -> Optional[Plugin]:
        """
        Imports a plugin as a module.

        :param folder: the folder to import the plugin from
        :return: the name of the imported module
        """
        module_name = f"{self.plugins_folder}.{folder}.init"
        try:
            imported = importlib.import_module(module_name, package=self.plugins_folder)
            logging.info(f"Imported plugin: {module_name}")
            return imported
        except Exception as e:
            print(e)
