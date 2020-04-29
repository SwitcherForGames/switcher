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
import difflib
import json
import os
from pathlib import Path
from typing import Dict, Optional

import requests
from scheduler.Scheduler import Scheduler

from api.PathEvaluator import PathEvaluator

url = "https://switcherforgames.com/api/switcher/magic-link-post"


async def post_data(code: str, data: str) -> None:
    """
    Posts the data to the server.

    Parameters
    ----------
    code : str
        The "magic link" authorisation code.
    data : str
        The string representation of the JSON data.
    """
    scheduler = Scheduler(run_in_thread=True)

    r = (await scheduler.map(_do_post, args=[(code, data,)]))[0]
    print(r.status_code, r.reason)


def _do_post(code, data) -> requests.Response:
    r = requests.post(url, data, headers={"MagicLinkCode": code})
    return r


def get_json(game: str, game_path: str) -> str:
    json_data: str = json.dumps(_get_data_dict(game, game_path))
    return json_data


def _get_data_dict(game: str, game_path: str) -> Dict:
    data = {
        "username": PathEvaluator().username(),
        "game": game,
        "gamePath": game_path,
        "executablePath": _find_executable(game_path, game),
    }

    return data


def _find_executable(filepath: str, game: str) -> Optional[str]:
    """
    Finds the most promising executable within a game folder.

    It will prioritise:
        1. Executables within a folder containing "bin" or "win".
        2. Executables with similar names to the game name.
        3. Executables without "unins" in their name, as these are usually uninstallers.

    Parameters
    ----------
    filepath : str
        The absolute path to the game folder being examined.
    game : str
        The name of the game, used to match against possible executables.

    Returns
    -------
    Optional[str]
        The absolute path to the most likely game executable, or None if there are no executables in the game folder.
    """
    executables = []

    # Find all executables within the game folder.
    for f in Path(filepath).rglob("*.exe"):
        executables.append(f"{f.absolute()}")

    # If possible, remove all executables not within a "bin" or "win" folder.
    if bin_or_win := list(
        filter(lambda e: "bin" in e or "win" in e.lower(), executables)
    ):
        executables = bin_or_win

    # Sort the executables by their similarity to the game name.
    executables = sorted(
        executables,
        key=lambda f: difflib.SequenceMatcher(None, game, f).ratio(),
        reverse=True,
    )

    # If possible, remove uninstall executables.
    if not_uninstall := list(
        filter(lambda e: "unins" not in os.path.split(e)[-1].lower(), executables)
    ):
        executables = not_uninstall

    if executables:
        out = executables[0]
        print(out)

        return out

    return None
