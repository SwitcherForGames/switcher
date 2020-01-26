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
from src.api.Platform import Platform


class Plugin:
    def __init__(self, platform: Platform):
        self.platform = platform

    def identify(self, filepath: str) -> bool:
        r"""
        Identify whether a particular file path belongs to the game handled by this plugin.

        This should return True when the full path to the folder containing the game is supplied as a parameter.
        For example, "D:\Program Files\SteamLibrary\steamapps\common\War Thunder" would return True for a
        War Thunder plugin but "D:\Program Files\SteamLibrary\steamapps\common\War Thunder\win64" should not.

        :param filepath: the path to the folder being examined
        :return: whether the path belongs to the desired game
        """
        raise NotImplementedError()

    def save_profile(self, *types) -> None:
        """
        Saves a profile for the current settings.

        :param types: the types of profile to save; e.g. graphics and/or keymap profiles
        """
        raise NotImplementedError()

    def get_executable(self) -> str:
        """
        :return: the path to the executable which launches the game
        """
        raise NotImplementedError()

    def is_windows(self) -> bool:
        return self.platform == Platform.WINDOWS

    def is_mac(self) -> bool:
        return self.platform == Platform.MAC_OS

    def is_linux(self) -> bool:
        return self.platform == Platform.LINUX
