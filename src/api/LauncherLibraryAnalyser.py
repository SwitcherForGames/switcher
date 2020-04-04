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


def get_all() -> Tuple["LauncherLibraryAnalyser", ...]:
    return (
        SteamLibraryAnalyser(),
        UbisoftLibraryAnalyser(),
        GOGLibraryAnalyser(),
    )


class LauncherLibraryAnalyser(ABC):
    def find_games(self, library_folder: str) -> Dict[str, str]:
        games_folder = self.get_game_folder(library_folder)
        games = {}

        if self.is_correct_launcher(library_folder) and os.path.exists(games_folder):
            for f in [join(games_folder, i) for i in os.listdir(games_folder)]:
                if not self.is_empty(f):
                    _, name = os.path.split(f)
                    games[f] = name

        return games

    @abstractmethod
    def is_correct_launcher(self, folder_in_program_files: str) -> bool:
        pass

    @abstractmethod
    def get_game_folder(self, folder_in_program_files: str) -> str:
        pass

    def is_empty(self, folder) -> bool:
        return not bool(os.listdir(folder))


class SteamLibraryAnalyser(LauncherLibraryAnalyser):
    def is_correct_launcher(self, folder_in_program_files: str) -> bool:
        _, name = os.path.split(folder_in_program_files)
        return "steam" in name.lower()

    def get_game_folder(self, folder_in_program_files: str) -> str:
        return join(folder_in_program_files, "steamapps", "common")


class UbisoftLibraryAnalyser(LauncherLibraryAnalyser):
    def is_correct_launcher(self, folder_in_program_files: str) -> bool:
        _, name = os.path.split(folder_in_program_files)
        return "ubisoft" in name.lower() or "uplay" in name.lower()

    def get_game_folder(self, folder_in_program_files: str) -> str:
        return join(folder_in_program_files, "games")


class GOGLibraryAnalyser(LauncherLibraryAnalyser):
    def is_correct_launcher(self, folder_in_program_files: str) -> bool:
        _, name = os.path.split(folder_in_program_files)
        return "GOGLibrary" in name

    def get_game_folder(self, folder_in_program_files: str) -> str:
        return folder_in_program_files
