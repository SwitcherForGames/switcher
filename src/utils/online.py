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
from typing import Tuple, List

from github import Github
from github.GitRelease import GitRelease
from github.PaginatedList import PaginatedList

whitelist = {"SwitcherForGames": "Switcher For Games"}
blacklist = []

template = "Switcher plugin for "
g = Github()


def find_online_plugins() -> Tuple[List, List]:
    """
    Finds available plugins from GitHub.

    Returns
    -------
    trusted : List
        List containing trusted plugins, published by SwitcherForGames.
    untrusted : List
        List containing untrusted plugins, published by the community.
    """
    plugins = search_plugins()
    for p in plugins:
        description = p.description

        if len(description) > len(template):
            game = description[len(template) :]

            # Remove full stop if it exists.
            if game.endswith("."):
                game = game[:-1]
        else:
            game = description

        p.game = game
        p.author = p.owner.login

        if alias := whitelist.get(p.author):
            p.author = alias

    trusted = [
        p
        for p in plugins
        if p.owner.login in whitelist and p.owner.login not in blacklist
    ]
    untrusted = [
        p for p in plugins if p not in trusted and p.owner.login not in blacklist
    ]

    for _list in (trusted, untrusted):
        _list.sort(key=lambda f: f.game)

    return trusted, untrusted


def search_plugins() -> PaginatedList:
    repos = g.search_repositories(query="topic:switcher-plugin")
    return repos


def get_switcher_releases() -> List[GitRelease]:
    repo = g.get_repo("SwitcherForGames/switcher")
    releases = repo.get_releases()

    return releases
