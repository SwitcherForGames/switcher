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
import logging
from typing import Optional

import requests
from requests import Response

url = "https://switcherforgames.com/api/switcher/dev-get-plugin-yaml"


def get_plugin_yaml_text(code: str) -> Optional[str]:
    response: Response = requests.get(f"{url}?code={code}")
    logging.info(f"Dev-install request: {response.status_code}, {response.reason}")

    yaml: str = response.text
    return yaml
