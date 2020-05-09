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
import logging
import os
import shutil
import sys
import uuid
import zipfile
from difflib import SequenceMatcher
from io import BytesIO
from os.path import join
from typing import Optional, List, Dict

import requests
import yaml

from api import files
from api.CodelessPlugin import CodelessPlugin
from api.Keys import Keys
from api.Platform import Platform
from api.Plugin import Plugin
from api.files import make_path
from api.profiles import Profile
from utils import online


class PluginHandler:
    """
    Class which handles importing plugins.
    """

    plugins_folder: str = files.plugins_path()
    profiles_folder: str = files.profile_path()
    sys.path.append(plugins_folder)

    def __init__(self):
        self.plugins: List[Plugin] = []

    def initialise(self) -> None:
        data = self.load_yaml()
        if not data.get("gamePaths"):
            data["gamePaths"] = {}

        for folder in os.listdir(self.plugins_folder):
            if not os.path.isdir(join(self.plugins_folder, folder)):
                continue

            plugin = None

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
                plugin.game_path = data.get("gamePaths").get(plugin.get_uid())

    def import_plugin_module(self, folder: str) -> Optional[Plugin]:
        """
        Imports a plugin as a module.

        :param folder: the folder to import the plugin from
        :return: the name of the imported module
        """
        module_name = f"plugins.{folder}.init"
        import importlib.util

        try:
            spec = importlib.util.spec_from_file_location(
                module_name, join(self.plugins_folder, folder, "init.py")
            )

            imported = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(imported)

            logging.info(f"Imported plugin: {module_name}")
            return imported
        except Exception as e:
            print(e)
            logging.error(e)

    def apply_changes(self, changes: Dict[str, bool]) -> None:
        install = [key for key, value in changes.items() if value]
        uninstall = [key for key, value in changes.items() if not value]

        for p in install:
            self.install_plugin(p)

        for p in uninstall:
            self.uninstall_plugin(p)

    def install_plugin(self, url: str) -> None:
        zipball = f"{url}/zipball/master"
        print(f"Downloading plugin from {zipball}")

        request = requests.get(zipball)
        zip = zipfile.ZipFile(BytesIO(request.content))
        target = zip.namelist()[0]

        zip.extractall(self.plugins_folder)
        print(f"Downloaded plugin to {target}")

        with open(join(self.plugins_folder, target, "plugin.yaml"), "r") as f:
            data = yaml.safe_load(f)
            dir_name = data[Keys.PACKAGE_NAME.value]

        shutil.move(
            join(self.plugins_folder, target), join(self.plugins_folder, dir_name)
        )
        self.save_installed_plugin_url(url, dir_name)

    def dev_install_plugin(self, yaml_text: str) -> None:
        """
        Installs a plugin in developer mode, when supplied with the text
        of its YAML file as a string.

        Parameters
        ----------
        yaml_text : str
            The access code for the plugin.
        """
        logging.info(f"Installing plugin in development mode: {yaml_text}.")
        target = f"DEV-{uuid.uuid4()}"

        target_dir = join(self.plugins_folder, target)
        os.makedirs(target_dir)

        with open(join(target_dir, "plugin.yaml"), "w+") as f:
            f.write(yaml_text)

        self.save_installed_plugin_url(target, target)

    async def suggest_plugins(self, games: Dict[str, str]) -> List[str]:
        trusted, _ = online.find_online_plugins()
        threshold = 0.9

        install = []
        for plugin in trusted:
            matches = []

            for loc, game in games.items():
                match = SequenceMatcher(None, plugin.game, game).ratio()
                matches.append(match)

                if match >= 1:
                    break
                elif (
                    match < threshold
                    and plugin.game in game
                    or plugin.game.replace(":", "") in game.replace(":", "")
                ):
                    matches.append(threshold)

            if max(matches) >= threshold:
                install.append(plugin)

        installed_plugin_urls = self.get_installed_plugin_urls()
        return [p.url for p in install if p.url not in installed_plugin_urls]

    def uninstall_plugin(self, url: str) -> None:
        target = self.load_yaml()["urls"][url]
        shutil.rmtree(join(self.plugins_folder, target))

        self.save_uninstalled_plugin_url(url)
        print(f"Removed plugin at {target}.")

    def get_installed_plugin_urls(self) -> List[str]:
        return self.load_yaml().get("urls") or []

    def save_installed_plugin_url(self, url: str, dir: str):
        data = self.load_yaml()

        data["urls"][url] = dir
        self.save_yaml(data)

    def save_uninstalled_plugin_url(self, url: str):
        data = self.load_yaml()

        del data["urls"][url]
        self.save_yaml(data)

    def save_game_path(self, path: str, plugin: Plugin) -> None:
        """
        Saves the path to the game associated with a plugin.

        :param path: the absolute file path to the game's root folder
        :param plugin: the plugin which handles the game
        """
        plugin.game_path = path

        data = self.load_yaml()
        if not data.get("gamePaths"):
            data["gamePaths"] = {}

        data["gamePaths"][plugin.get_uid()] = path
        self.save_yaml(data)

    def _get_profile_path(self, plugin: Plugin, profile: Profile) -> str:
        base_plugin_profile_dir = make_path(
            join(self.profiles_folder, plugin.get_uid())
        )
        target_dir = make_path(join(base_plugin_profile_dir, profile.uuid))
        return target_dir

    def save_profile(self, plugin: Plugin, profile: Profile) -> None:
        target_dir = self._get_profile_path(plugin, profile)
        plugin.save(profile, target_dir)

    def apply_profile(self, plugin: Plugin, profile: Profile) -> None:
        target_dir = self._get_profile_path(plugin, profile)
        plugin.apply(profile, target_dir)

    def delete_profile(self, plugin: Plugin, profile: Profile) -> None:
        target_dir = self._get_profile_path(plugin, profile)
        plugin.delete(profile, target_dir)

    def get_profiles(self, plugin: Plugin) -> List[Profile]:
        profile_dir = make_path(join(self.profiles_folder, plugin.get_uid()))

        return plugin.get_profiles(profile_dir)

    def load_yaml(self) -> Dict:
        yaml_path = self._yaml_path()
        if "plugins.yaml" not in os.listdir(self.plugins_folder):
            with open(yaml_path, "w") as f:
                data = {"urls": {}}
                yaml.safe_dump(data, f)

        with open(yaml_path, "r") as f:
            return yaml.safe_load(f)

    def save_yaml(self, data: Dict) -> None:
        with open(self._yaml_path(), "w") as f:
            yaml.safe_dump(data, f)

    def _yaml_path(self) -> str:
        folder = self.plugins_folder
        yaml_file = join(folder, "plugins.yaml")
        return yaml_file
