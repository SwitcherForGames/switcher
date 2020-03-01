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
from os.path import join

from api.Platform import Platform


def make_path(path: str) -> str:
    try:
        os.makedirs(path)
    except FileExistsError:
        pass
    return path


_platform = Platform.get()
_username = os.environ.get("USERNAME") or os.environ.get("USER")

if _platform is Platform.WINDOWS:
    _safe_path = make_path(f"C:\\Users\\{_username}\\AppData\\Roaming\\Switcher")
else:
    _safe_path = make_path(r"~/.switcher")


def plugins_path() -> str:
    return make_path(join(_safe_path, "plugins"))


def profile_path() -> str:
    return make_path(join(_safe_path, "profiles"))


def log_path() -> str:
    return join(_safe_path, "switcher.log")
