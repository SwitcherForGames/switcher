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
import shutil
from enum import Enum
from os.path import join
from typing import Union, List

from api.PathEvaluator import PathEvaluator
from api.Platform import Platform

_safe_path = None


def init(dev: bool) -> None:
    global _safe_path

    if dev:
        _switcher_folder = "SwitcherDev"
    else:
        _switcher_folder = "Switcher"

    if _platform is Platform.WINDOWS:
        _safe_path = make_path(
            f"C:\\Users\\{_username}\\AppData\\Roaming\\{_switcher_folder}"
        )
    else:
        _safe_path = make_path(f"~/.{_switcher_folder.lower()}")


def make_path(path: str) -> str:
    try:
        os.makedirs(path)
    except FileExistsError:
        pass
    return path


_platform = Platform.get()
_evaluator = PathEvaluator.create(_platform)
_username = _evaluator.username()


def plugins_path() -> str:
    return make_path(join(_safe_path, "plugins"))


def profile_path() -> str:
    return make_path(join(_safe_path, "profiles"))


def log_path() -> str:
    return join(_safe_path, "switcher.log")


tag = "$!"  # Denotes part of a path as a variable.


class PathVariable(Enum):
    DOCUMENTS = "DOCUMENTS"
    USERNAME = "USERNAME"
    HOME = "HOME"

    @staticmethod
    def get(value: str) -> "PathVariable":
        for var in PathVariable:
            if var.value == value:
                return var


class FilePathParsingException(Exception):
    pass


def evaluate_path(path: Union[str, List[str]]) -> Union[Union[List[str], str]]:
    """
    Interprets a file path, translating special variables to create the real path for the current system.

    :param path: the file path to interpret
    :return: the real path for the current system
    """
    if isinstance(path, List):
        return [evaluate_path(p) for p in path]

    if not path or tag not in path:
        return path

    opening = path.count(tag)
    closing = path.count(tag[::-1])

    if opening != closing:
        raise FilePathParsingException(
            f"Tags do not match. There must be a closing tag for each opening tag.\n\n"
            f"Problematic path: {path}"
        )

    spl_open = path.split(tag)
    spl_closed = [p.split(tag[::-1])[0] for p in spl_open if tag[::-1] in p]

    for str_var in spl_closed:
        variable: PathVariable = PathVariable.get(str_var)
        out = _evaluator.evaluate(variable)

        if not out:
            raise FilePathParsingException(
                f"Could not evaluate path variable {str_var=}."
            )

        path = path.replace(f"{tag}{str_var}{tag[::-1]}", out)

    return path


def sanitise_abs_path_for_profile(_path: str) -> str:
    if _platform is Platform.WINDOWS:
        return _path.replace(":", "")
    else:
        return f"root{_path}"


def _copyfiles(
    from_path: str,
    to_path: str,
    item_paths: Union[List[str], str],
    creating_profile: bool,
) -> None:
    if not isinstance(item_paths, List):
        item_paths = [
            item_paths,
        ]

    # In some cases, the game may have different folder names depending on the version or system.
    # We only want to raise an exception if *none* of the operations succeed.
    exceptions = []
    success = False

    for p in item_paths:
        try:
            _copyfile(from_path, to_path, p, creating_profile)
            success = True
        except Exception as e:
            exceptions.append(e)

    if not success:
        for e in exceptions:
            raise e


def _copyfile(
    from_path: str, to_path: str, item_path: str, creating_profile: bool
) -> None:
    # If the item_path is an absolute path, it's independent of the game folder and needs to be handled separately.
    if os.path.isabs(item_path):
        relative = sanitise_abs_path_for_profile(item_path)

        # If we're creating a profile, the 'from' path points to the absolute item path
        # and the 'to' path points to the profile path joined with the sanitised item path.
        if creating_profile:
            _from = item_path
            _to = join(to_path, relative)
        else:
            # If we're not creating a profile, the 'from' and 'to' paths are reversed.
            _from = join(from_path, relative)
            _to = item_path

    else:  # If the item_path is relative, the situation is much simpler.
        _from = join(from_path, item_path)
        _to = join(to_path, item_path)

    try:
        if not os.path.isdir(_to):
            folder, _ = os.path.split(_to)
        else:
            folder = _to

        os.makedirs(folder)
    except FileExistsError:
        pass

    if os.path.isdir(_from):
        if os.path.exists(_to):
            shutil.rmtree(_to)

        shutil.copytree(_from, _to)
    else:
        shutil.copyfile(_from, _to)

    print(f"Copied '{_from}' to '{_to}'.")
