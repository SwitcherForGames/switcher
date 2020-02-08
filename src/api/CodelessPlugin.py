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

from src.api.Keys import Keys
from src.api.Plugin import Plugin


class CodelessPlugin(Plugin):
    """
    Plugin class which implements a "codeless" plugin with no custom code.

    Codeless plugins only require a YAML file to define their functionality.
    """

    def initialise(self) -> None:
        config_defined: bool = self.yaml.get(Keys.GRAPHICS_CONFIG) or self.yaml.get(
            Keys.KEYMAP_CONFIG
        )
        assert (
            config_defined
        ), "Codeless plugins must define at least the location of the graphics config or the keymap config."

    def verify(self, folder_path: str) -> bool:
        paths = self.yaml.get(Keys.VERIFICATION_PATHS)
        assert paths, (
            "Verification paths have not been defined. These are required to check if the game exists at a "
            "location. "
        )

        here = self.here()
        return all([os.path.exists(os.path.join(here, p)) for p in paths])

    def get_executable(self) -> str:
        pass

    def save_profile(self, *types) -> None:
        pass  # TODO: implement
