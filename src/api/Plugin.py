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
import inspect
import logging
import os
from abc import ABC, abstractmethod
from os import path
from typing import Dict, Optional, final

import yaml
from pip._vendor import requests
from scheduler.Scheduler import Scheduler

from src.api.Platform import Platform


class Plugin(ABC):
    """
    Abstract plugin class which will be inherited from by plugin implementations.
    """

    def __init__(self, platform: Platform):
        super(Plugin, self).__init__()
        self.platform = platform
        self.yaml = self.load_yaml()
        self.initialise()

    @abstractmethod
    def initialise(self) -> None:
        pass

    @abstractmethod
    def identify(self, folder_path: str) -> bool:
        r"""
        Identify whether a particular (absolute) file path belongs to the game handled by this plugin.

        This should return True when the full path to the folder containing the game is supplied as a parameter.
        For example, "D:\Program Files\SteamLibrary\steamapps\common\War Thunder" would return True for a
        War Thunder plugin but "D:\Program Files\SteamLibrary\steamapps\common\War Thunder\win64" should not.

        :param folder_path: the path to the folder being examined
        :return: whether the path belongs to the desired game
        """
        pass

    @abstractmethod
    def save_profile(self, *types) -> None:
        """
        Saves a profile for the current settings.

        :param types: the types of profile to save; e.g. graphics and/or keymap profiles
        """
        pass

    @abstractmethod
    def get_executable(self) -> str:
        """
        :return: the path to the executable which launches the game
        """
        pass

    def load_yaml(self) -> Dict:
        folder_location = self.here()
        yaml_location = path.join(folder_location, "plugin.yaml")

        with open(yaml_location, "r") as stream:
            return yaml.safe_load(stream)

    @final
    async def get_header(self) -> Optional[str]:
        """
        Gets the path to the  header image. If it needs to be downloaded, it will download the image first.

        :return: the absolute file path to the header image
        """
        items = os.listdir(self.here())
        stripped = [path.splitext(i)[0] for i in items]
        header = "header"

        # Check if header already exists.
        if header in stripped:
            name = items[stripped.index(header)]
            return path.join(self.here(), name)

        return await self._download_header()

    async def _download_header(self) -> Optional[str]:
        """
        Downloads the header image. By default it will use the image from the Steam page.

        :return: the absolute file path to the downloaded header image
        """
        steam_id = self.yaml.get("steamID")
        if not steam_id:
            return None

        url = f"http://cdn.akamai.steamstatic.com/steam/apps/{steam_id}/header.jpg"
        self.scheduler = Scheduler()
        self.scheduler.add(target=self._perform_download, args=(url, "header"))
        result = await self.scheduler.run()
        return result[0]

    def _perform_download(self, url: str, filename: str, ext: str = "jpg") -> str:
        logging.info(f"Downloading header image from {url} as {filename}")
        data = requests.get(url).content
        filepath = f"{path.join(self.here(), filename)}.{ext}"
        with open(filepath, "wb") as handler:
            handler.write(data)

        return filepath

    @final
    def here(self) -> str:
        """
        Returns the absolute path to the folder containing the current plugin class.

        NOTE: '__file__' cannot be used because it returns the path to the abstract Plugin class,
        not the desired plugin implementation.
        """
        class_location = inspect.getfile(self.__class__)
        return path.abspath(path.dirname(class_location))

    @final
    def get_name(self) -> str:
        return self.yaml.get("game")

    @final
    def get_api_level(self) -> int:
        return self.yaml.get("api")

    @final
    def is_windows(self) -> bool:
        return self.platform == Platform.WINDOWS

    @final
    def is_mac(self) -> bool:
        return self.platform == Platform.MAC_OS

    @final
    def is_linux(self) -> bool:
        return self.platform == Platform.LINUX
