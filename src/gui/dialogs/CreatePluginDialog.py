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
import asyncio

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QListWidget, QPushButton, QLabel, QProgressBar

from api.GameFinder import GameFinder
from utils import resources, magic_link


class CreatePluginDialog(QDialog):
    def __init__(self, application, game_finder, code: str = None):
        super().__init__()

        self.game_finder: GameFinder = game_finder
        self.application = application
        self.code = code

        self.list_games: QListWidget = None
        self.btn_next: QPushButton = None
        self.btn_close: QPushButton = None

        self.lbl_connecting: QLabel = None
        self.lbl_done: QLabel = None
        self.lbl_instructions: QLabel = None
        self.progress_connecting: QProgressBar = None

        uic.loadUi(resources.get_create_plugin_dialog_layout(), self)

        self.progress_connecting.setVisible(False)
        self.lbl_connecting.setVisible(False)
        self.lbl_done.hide()
        self.btn_close.hide()

        self.btn_close.clicked.connect(lambda _: self.accept())
        self.btn_next.clicked.connect(self.on_next_clicked)

        self.setWindowTitle("Create a plugin")
        self.games = {}

        asyncio.ensure_future(self.coro_update_listwidget())

    async def coro_update_listwidget(self):
        self.games = await self.game_finder.coro_find_games()

        for location, name in self.games.items():
            self.list_games.addItem(name)

    def on_next_clicked(self) -> None:
        game = self.list_games.selectedItems()[0].text()
        path = [k for k, v in self.games.items() if v == game][0]

        json = magic_link.get_json(game, path)
        asyncio.ensure_future(self.push_data(json))

        self.list_games.hide()
        self.lbl_instructions.hide()
        self.setFixedSize(360, 200)

        self.btn_next.hide()
        self.progress_connecting.setVisible(True)
        self.lbl_connecting.setVisible(True)

    async def push_data(self, json: str) -> None:
        await magic_link.post_data(self.code, json)

        self.progress_connecting.hide()
        self.lbl_connecting.hide()
        self.list_games.hide()

        self.lbl_done.show()
        self.btn_close.show()
