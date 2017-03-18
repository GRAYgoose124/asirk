#!python
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
import uvloop
import os

from bot import Irk

logging.basicConfig(level=logging.INFO, format='[%(levelname)7s] %(name)7s:%(lineno)4s |%(message)s')
logger = logging.getLogger(__name__)


def main():
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    # Plugin path set static with 'python asirk' with cwd in mind.
    config = {
            'host': b'irc.supernets.org', 'port': b'6667', 'ssl': False,
            'nick': 'ducky', 'pass': '',
            'ident': '', 'user': 'ducky',
            'mode': '+B', 'unused': '*',
            'owner': 'mrsnafu', 'owner_email': '',
            'channels': ['#snafu'], 'plugin_path': os.path.join(os.getcwd(), 'asirk', 'plugins')
    }

    asirk = Irk(loop, config)

    asirk.start()

    loop.run_until_complete(asirk.client_completed)


if __name__ == '__main__':
    main()
