#   asIrk: asyncio irc bot
#   Copyright (C) 2017  Grayson Miller
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>
import json
import os
import os.path
from pathlib import Path
import sys
import asyncio
import logging
import argparse

from .core.bot import Irk
from .core.config import load_config

from .utils import createDefaultConfig, useUVloop

log = logging.getLogger(__name__)


def args():
    parser = argparse.ArgumentParser(description="asyncio irc bot.")
    return parser.parse_args()


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname).1s [%(name)15.15s]: %(lineno)4s |%(message)s",
        datefmt="%H%M%S",
    )
    useUVloop()
    loop = asyncio.get_event_loop()

    home_path = Path(__file__).parent
    data_path = home_path / "data"
    config_path = data_path / "config.json"
    plugin_path = home_path / "plugins"

    if not config_path.exists():
        createDefaultConfig(config_path)

    config = load_config(config_path)

    config["plugin_data_path"] = data_path

    asirk = Irk(loop, config, plugin_path)
    asirk.start()

    loop.run_until_complete(asirk.client_completed)


if __name__ == "__main__":
    main()
