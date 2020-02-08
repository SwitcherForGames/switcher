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

from api.Platform import Platform
from src.api.Keys import Keys
from src.api.Plugin import Plugin


class CodelessPlugin(Plugin):
    """
    Plugin class which implements a "codeless" plugin with no custom code.

    Codeless plugins only require a YAML file to define their functionality.
    """

    def __init__(self, platform: Platform, path: str):
        self.here = lambda: path
        super(CodelessPlugin, self).__init__(platform)

    def initialise(self) -> None:
        graphics: bool = self.get(Keys.GRAPHICS_CONFIG)
        keymap: bool = self.get(Keys.KEYMAP_CONFIG)

        error = "Codeless plugins must define at least the location of the graphics config or the keymap config."
        assert graphics or keymap, error

    def get_executable(self) -> str:
        pass

    def save_profile(self, *types) -> None:
        pass  # TODO: implement
