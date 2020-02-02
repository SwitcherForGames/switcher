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
from abc import ABC, abstractmethod
from os import path
from typing import Dict

import yaml

from src.api.Platform import Platform


class Plugin(ABC):
    """
    Abstract plugin class which will be inherited from by plugin implementations.
    """

    def __init__(self, platform: Platform):
        super(Plugin, self).__init__()
        self.platform = platform
        self.yaml = self.load_yaml()
        print(self.yaml)
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
        class_location = inspect.getfile(self.__class__)
        folder_location = path.abspath(path.dirname(class_location))
        yaml_location = path.join(folder_location, "plugin.yaml")

        with open(yaml_location, "r") as stream:
            return yaml.safe_load(stream)

    def get_name(self) -> str:
        return self.yaml["name"]

    def is_windows(self) -> bool:
        return self.platform == Platform.WINDOWS

    def is_mac(self) -> bool:
        return self.platform == Platform.MAC_OS

    def is_linux(self) -> bool:
        return self.platform == Platform.LINUX
