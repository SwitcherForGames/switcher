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
import sys
from typing import Optional

_args = sys.argv


def cleanup() -> None:
    global _args

    logging.info(f"Arguments before cleanup: {sys.argv}")
    blacklist = ("magic-link", "dev-install")

    args = list(filter(lambda a: not any([b in a for b in blacklist]), _args))
    sys.argv = args

    logging.info(f"Arguments after cleanup: {sys.argv}")
    _args = sys.argv


def magic_link() -> Optional[str]:
    """
    If Switcher was opened from the website with a "magic link", the code associated with the link
    will be returned.

    Returns
    -------
    link: str, None
        If there is a magic link, the code is returned; otherwise, None.
    """
    filt = list(filter(lambda a: "magic-link" in a, _args))

    if filt:
        argument = filt[0]
        code = argument.split("code=")[-1]

        logging.info(f"Found magic-link code: {code}")

        return code

    return None


def github_install_link() -> Optional[int]:
    """
    If Switcher was opened with a "install-plugin" link,
    the GitHub ID for the plugin's repository will be returned.

    Returns
    -------
    id: int, None
        The GitHub ID from the link if it exists; otherwise, None.
    """
    filt = list(filter(lambda a: "install-plugin" in a, _args))

    if filt:
        argument = filt[0]
        id = argument.split("github=")[-1]

        logging.info(f"Found install-plugin Github ID: {id}")

        try:
            return int(id)
        except:
            pass

    return None


def dev_install_link() -> Optional[str]:
    """
    If Switcher was opened with a "dev-install" link, the code associated with the link
    will be returned.

    Returns
    -------
    link: str, None
        The code from the link if it exists; otherwise, None.
    """
    filt = list(filter(lambda a: "dev-install" in a, _args))

    if filt:
        argument = filt[0]
        code = argument.split("code=")[-1]

        logging.info(f"Found dev-install code: {code}")

        return code

    return None
