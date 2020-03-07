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

from api.Platform import Platform


class PathEvaluator:
    def evaluate(self, var: "PathVariable") -> str:
        from api.files import PathVariable

        if self.is_pathvar(var, PathVariable.HOME):
            return self.home()
        elif self.is_pathvar(var, PathVariable.USERNAME):
            return self.username()
        elif self.is_pathvar(var, PathVariable.DOCUMENTS):
            return self.documents()

    def home(self) -> str:
        return os.path.expanduser("~")

    def username(self) -> str:
        return os.environ.get("USERNAME") or os.environ.get("USER")

    def documents(self) -> str:
        raise NotImplementedError()

    @staticmethod
    def create(platform: Platform) -> "PathEvaluator":
        if platform is Platform.WINDOWS:
            return WindowsEvaluator()
        elif platform is Platform.LINUX:
            return LinuxEvaluator()
        elif platform is Platform.MAC_OS:
            return MacEvaluator()

    def is_pathvar(self, var, pathvar) -> bool:
        return var.value == pathvar.value


class WindowsEvaluator(PathEvaluator):
    def documents(self) -> str:
        import ctypes
        from ctypes.wintypes import MAX_PATH

        dll = ctypes.windll.shell32
        buf = ctypes.create_unicode_buffer(MAX_PATH + 1)

        if dll.SHGetSpecialFolderPathW(None, buf, 0x0005, False):
            return buf.value

        raise Exception("Could not get Documents folder.")


class NixEvaluator(PathEvaluator):
    pass


class MacEvaluator(NixEvaluator):
    pass


class LinuxEvaluator(NixEvaluator):
    pass
