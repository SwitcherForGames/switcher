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
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QColor
from PyQt5.QtWidgets import QWidget, QGraphicsColorizeEffect

from api.Plugin import Plugin
from utils import resources

color1 = QColor(255, 255, 0)
strength1 = 0.05

color2 = QColor(0, 0, 0)
strength2 = 0.1


class PluginWidget(QWidget):
    def __init__(self, plugin: Plugin):
        super(PluginWidget, self).__init__()
        self.plugin = plugin
        uic.loadUi(resources.get_plugin_item_layout(), self)

        height = 215
        width = 460
        self.setFixedHeight(height)
        self.setFixedWidth(width)
        self.setContentsMargins(0, 0, 0, 0)

        self.setAutoFillBackground(True)

        self.indicator.setVisible(False)
        self.mousePressEvent = self.onclick

        self.exact_size = (width, height)

        self.active = False
        self.effect = self.get_effect()
        self.setGraphicsEffect(self.effect)

        self.on_activation_changed()

    async def coro_initialise(self) -> None:
        backgrnd = QPixmap(await self.plugin.get_header())
        backgrnd = backgrnd.scaled(self.size(), transformMode=Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(backgrnd))
        self.setPalette(palette)

        self.setGraphicsEffect(self.effect)

    def onclick(self, event):
        # self.indicator.setVisible(not self.indicator.isVisible())
        self.active = not self.active
        self.on_activation_changed()

    def on_activation_changed(self):
        if self.active:
            self.effect.setColor(color1)
            self.effect.setStrength(strength1)
        else:
            self.effect.setColor(color2)
            self.effect.setStrength(strength2)

    def get_effect(self):
        effect = QGraphicsColorizeEffect()
        effect.setColor(color2)
        effect.setStrength(strength2)
        return effect
