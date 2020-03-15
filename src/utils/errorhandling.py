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
import sys
from typing import Callable

subscribers = []


def add_hook(hook: Callable) -> None:
    subscribers.append(hook)


def remove_hook(hook: Callable) -> None:
    subscribers.remove(hook)


def init() -> None:
    sys.excepthook = hook


def hook(type, value, traceback):
    for s in subscribers:
        try:
            s(type, value, traceback)
        except:
            pass

    sys.__excepthook__(type, value, traceback)
