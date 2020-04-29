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
from typing import Optional

_args = sys.argv


def magic_link() -> Optional[str]:
    """
    If Switcher was opened from the website with a "magic link", the code associated with the link
    will be returned.

    Returns
    -------
    link: Optional[str]
        If there is a magic link, the code is returned; otherwise, None.
    """
    relevant = list(filter(lambda a: "magic-link" in a, _args))

    if relevant:
        argument = relevant[0]
        code = argument.split("code=")[-1]

        return code

    return None
