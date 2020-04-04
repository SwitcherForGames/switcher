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
from typing import Dict

import yaml

from api import files

_settings: "Settings" = None


def get_instance() -> "Settings":
    global _settings

    if not _settings:
        _settings = Settings()

    return _settings


class Settings:
    switcher_directory: str = files._switcher_directory
    last_update_check: float = 0
    new_release_tag: str = None
    version = 1

    def __init__(self):
        self.__config_path = files.settings_path()
        self.reload()

    def reload(self) -> None:
        if not os.path.exists(self.__config_path):
            self.commit()

        with open(self.__config_path, "r") as stream:
            data = yaml.safe_load(stream)
            self.set_fields(data)

    def commit(self) -> None:
        with open(self.__config_path, "w") as stream:
            data = self.get_fields()
            yaml.safe_dump(data, stream)

    def set_fields(self, fields: Dict) -> None:
        if fields:
            for key, value in fields.items():
                setattr(self, key, value)

    def get_fields(self) -> Dict:
        fields = [
            attr
            for attr in dir(self)
            if not callable(getattr(self, attr)) and not attr.startswith("_")
        ]
        out = {}

        for f in fields:
            out[f] = getattr(self, f)

        return out
