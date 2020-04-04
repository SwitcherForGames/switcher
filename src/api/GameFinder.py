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
import string
from abc import ABC, abstractmethod
from os.path import join
from typing import List, Dict

from scheduler.Scheduler import Scheduler

from api import LauncherLibraryAnalyser
from api.Platform import Platform


def get() -> "GameFinder":
    platform = Platform.get()

    if platform is Platform.WINDOWS:
        return WindowsGameFinder()
    else:
        raise NotImplementedError("Linux/macOS GameFinders not implemented yet.")


class GameFinder(ABC):
    def __init__(self):
        self.scheduler = Scheduler(run_in_thread=True)

    async def coro_find_games(self) -> Dict[str, str]:
        result = await self.scheduler.map(target=self.find_games, args=[(),])
        return result[0]

    @abstractmethod
    def find_games(self) -> Dict[str, str]:
        """
        Finds games on the system.

        Returns
        -------
        Dict[str, str]
            Dictionary whose keys are the paths to possible discovered games, and whose corresponding values are the
            names of the games.
        """


class WindowsGameFinder(GameFinder):
    def find_games(self) -> Dict[str, str]:
        drives = self.get_drives()
        games = {}

        for drive in drives:
            if folders := self.get_program_folders(drive):
                for program_files_folder in folders:
                    for possible_library_folder in [
                        join(program_files_folder, f)
                        for f in os.listdir(program_files_folder)
                    ]:

                        for analyser in LauncherLibraryAnalyser.get_all():
                            if found := analyser.find_games(possible_library_folder):
                                games = {**games, **found}

        return games

    def get_drives(self) -> List[str]:
        """
        Returns
        -------
        List[str]
            List containing all drives on the system (e.g. "C:", "D:").
        """
        return [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]

    def get_program_folders(self, drive: str) -> List[str]:
        out = []

        for f in os.listdir(drive):
            if "program files" in f.lower():
                out.append(join(drive, f))

        return out
