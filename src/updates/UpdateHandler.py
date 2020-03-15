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
import time

import yaml
from scheduler.Scheduler import Scheduler

from api import files
from updates.CleanupThread import CleanupThread
from utils import online, settings


def parse_checksum(text: str, filename: str) -> str:
    lines = text.splitlines(keepends=False)
    relevant_lines = [l for l in lines if filename in l and "`" in l]

    checksum = relevant_lines[-1].replace("`", "").split(" ")[0].strip()
    return checksum


class UpdateHandler:
    def __init__(self):
        self.scheduler = None
        self.cleanup_thread = None

        self.installer_folder = files.installer_path()
        self.prefs = settings.get_instance()

    def should_check_for_updates(self) -> bool:
        return time.time() - self.prefs.last_update_check > 3600 * 6

    async def get_latest_version(self):
        self.scheduler = Scheduler()
        releases = (
            await self.scheduler.map(target=online.get_switcher_releases, args=[()])
        )[0]

        self.prefs.last_update_check = time.time()
        self.prefs.commit()

        return releases[0]

    def get_current_version(self) -> str:
        with open("manifest.yaml", "r") as f:
            data = yaml.safe_load(f)

            return data.get("version")

    def cleanup(self) -> None:
        self.cleanup_thread = CleanupThread(
            self.installer_folder, self.get_current_version()
        )
        self.cleanup_thread.start()
