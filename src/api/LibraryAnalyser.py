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
import os
from abc import ABC, abstractmethod
from os.path import join
from typing import Dict, Tuple


def get_all() -> Tuple["LibraryAnalyser", ...]:
    """
    Gets all the library analysers which have been implemented.

    Returns
    -------
    Tuple[LibraryAnalyser, ...]
        Tuple containing all LibraryAnalysers available.
    """
    return (
        SteamLibraryAnalyser(),
        UbisoftLibraryAnalyser(),
        GOGLibraryAnalyser(),
        EpicLibraryAnalyser(),
    )


class LibraryAnalyser(ABC):
    """
    Class used to find games on the system.
    """

    def find_games(self, folder_in_program_files: str) -> Dict[str, str]:
        """
        Finds games in a given possible library folder.

        Parameters
        ----------
        folder_in_program_files : str
            A folder within a folder containing programs, like "Program Files" on Windows,
            which may or may not be a game library.

        Returns
        -------
        Dict[str, str]
            Dictionary whose keys are the absolute paths to the games, and whose values are
            the name of the game folders.
        """
        games_folder = self.get_game_folder(folder_in_program_files)
        games = {}

        if self.is_correct_launcher(folder_in_program_files) and os.path.exists(
            games_folder
        ):
            for f in [join(games_folder, i) for i in os.listdir(games_folder)]:
                if not self.is_empty(f):
                    _, name = os.path.split(f)
                    games[f] = name

        return games

    @abstractmethod
    def is_correct_launcher(self, folder_in_program_files: str) -> bool:
        """
        Checks whether a possible library folder appears to belong to the launcher handled
        by the current implementation.

        Parameters
        ----------
        folder_in_program_files : str
            The path to the folder, which is inside a folder like "Program Files" on Windows.

        Returns
        -------
        bool
            Whether the folder is probably a library folder belonging to the current launcher.
        """

    @abstractmethod
    def get_game_folder(self, folder_in_program_files: str) -> str:
        """
        When provided with the root folder for a game library, returns the path to the folder which contains
        the actual games. For example, in Steam games are saved to "SteamLibrary/steamapps/common".

        Parameters
        ----------
        folder_in_program_files : str
            The path to the probably library folder, which is inside a folder like "Program Files" on Windows.

        Returns
        -------
        str
            The path to the folder containing the games stored in the library.
        """

    def is_empty(self, folder) -> bool:
        """

        Parameters
        ----------
        folder : str
            The path to the folder.

        Returns
        -------
        bool
            Whether the folder is empty.
        """
        return not bool(os.listdir(folder))


class SteamLibraryAnalyser(LibraryAnalyser):
    """
    Library analyser for Steam.
    """

    def is_correct_launcher(self, folder_in_program_files: str) -> bool:
        _, name = os.path.split(folder_in_program_files)
        return "steam" in name.lower()

    def get_game_folder(self, folder_in_program_files: str) -> str:
        return join(folder_in_program_files, "steamapps", "common")


class UbisoftLibraryAnalyser(LibraryAnalyser):
    """
    Library analyser for Uplay.
    """

    def is_correct_launcher(self, folder_in_program_files: str) -> bool:
        _, name = os.path.split(folder_in_program_files)
        return "ubisoft" in name.lower() or "uplay" in name.lower()

    def get_game_folder(self, folder_in_program_files: str) -> str:
        if os.path.exists(games := join(folder_in_program_files, "games")):
            return games

        return folder_in_program_files


class GOGLibraryAnalyser(LibraryAnalyser):
    """
    Library analyser for GOG Galaxy.
    """

    def is_correct_launcher(self, folder_in_program_files: str) -> bool:
        _, name = os.path.split(folder_in_program_files)
        return "GOGLibrary" in name

    def get_game_folder(self, folder_in_program_files: str) -> str:
        return folder_in_program_files


class EpicLibraryAnalyser(LibraryAnalyser):
    """
    Library analyser for the Epic Games Launcher.
    """

    def is_correct_launcher(self, folder_in_program_files: str) -> bool:
        _, name = os.path.split(folder_in_program_files)
        return "epic" in name.lower()

    def get_game_folder(self, folder_in_program_files: str) -> str:
        return folder_in_program_files
