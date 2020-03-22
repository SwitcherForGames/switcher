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


def is_pathvar(var, pathvar) -> bool:
    return var.value == pathvar.value


class PathEvaluator:
    def evaluate(self, var: "PathVariable") -> str:
        from api.files import PathVariable

        if is_pathvar(var, PathVariable.HOME):
            return self.home()
        elif is_pathvar(var, PathVariable.USERNAME):
            return self.username()
        elif is_pathvar(var, PathVariable.DOCUMENTS):
            return self.documents()
        elif is_pathvar(var, PathVariable.DESKTOP):
            return self.desktop()

    def home(self) -> str:
        return os.path.expanduser("~")

    def username(self) -> str:
        return os.environ.get("USERNAME") or os.environ.get("USER")

    def documents(self) -> str:
        raise NotImplementedError()

    def desktop(self) -> str:
        raise NotImplementedError()

    @staticmethod
    def create(platform: Platform) -> "PathEvaluator":
        if platform is Platform.WINDOWS:
            return WindowsEvaluator()
        elif platform is Platform.LINUX:
            return LinuxEvaluator()
        elif platform is Platform.MAC_OS:
            return MacEvaluator()


class WindowsEvaluator(PathEvaluator):
    def __init__(self):
        import winshell

        self.winshell = winshell

    def documents(self) -> str:
        return self.winshell.my_documents()

    def desktop(self) -> str:
        return self.winshell.desktop()


class NixEvaluator(PathEvaluator):
    def desktop(self) -> str:
        return join(self.home(), "Desktop")

    def documents(self) -> str:
        return join(self.home(), "Documents")


class LinuxEvaluator(NixEvaluator):
    pass


class MacEvaluator(NixEvaluator):
    pass
