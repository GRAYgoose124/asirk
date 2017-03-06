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
import logging
import asyncio
import os

from bot import Irk


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main():
    loop = asyncio.get_event_loop()

    # Plugin path set static with 'python asirk' from wd in mind.
    config = {
            'host': b'irc.foonetic.net', 'port': b'6697', 'ssl': True,
            'nick': 'Duckborg', 'pass': 'fxcva',
            'ident': '', 'user': 'Duckborg',
            'mode': '+B', 'unused': '*',
            'owner': 'graygoose124', 'owner_email': '',
            'channels': ['#testgrounds'], 'plugin_path': os.path.join(os.getcwd(), 'asirk', 'plugins')
    }

    asirk = Irk(loop, config)

    asirk.start()

    loop.run_until_complete(asirk.client_completed)


if __name__ == '__main__':
    main()
