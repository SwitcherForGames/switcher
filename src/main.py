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
import logging
import multiprocessing
import os
import signal
import sys
from os import path
from pathlib import Path

from qasync import QEventLoop

from api import files

# Whether running in development mode.
dev = not getattr(sys, "frozen", False)
files.init(dev)

from gui.Application import Application
from utils import errorhandling

if __name__ == "__main__":
    # Fix issues when packaged with PyInstaller.
    multiprocessing.freeze_support()

    # Initialise logging.
    logging.basicConfig(filename="switcher.log", level=logging.DEBUG)

    # Fix Ctrl-C behaviour with PyQt.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Fix error handling with PyQt on Windows.
    errorhandling.init()

    # Set the working directory for consistency.
    if not dev:
        # When packaged using PyInstaller.
        location = os.path.abspath(sys._MEIPASS)
    else:
        # When running as a normal Python program.
        location = Path(path.abspath(path.dirname(__file__))).parent

    os.chdir(location)
    sys.path.append(os.getcwd())

    app = Application(sys.argv)

    # Setup asyncio to work with PyQt.
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # Open the launcher window. Must be called after setting the event loop.
    app.launch()

    with loop:
        sys.exit(loop.run_forever())
