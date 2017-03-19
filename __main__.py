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
import os
import asyncio
import logging
import argparse 

logging.basicConfig(level=logging.INFO, format='[%(levelname)7s] %(name)7s:%(lineno)4s |%(message)s')
logger = logging.getLogger(__name__)

if os.name != 'nt':
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except:
        logger.warn("Not using uvloop!")

from bot import Irk
from config import load_config, save_config


def main():
    loop = asyncio.get_event_loop()

    home_path = os.path.join(os.getcwd(), 'asirk')    
    data_path = os.path.join(home_path, 'data')

    config_path = os.path.join(data_path, 'config.json')
    plugin_path = os.path.join(data_path, 'plugins')

    config = load_config(config_path)

    # asyncio Protocols requires b'host:port' format.    
    config['host'] = bytes(config['host'], 'utf-8')
    config['port'] = bytes(config['port'], 'utf-8')
    config['plugin_path'] = plugin_path
    
    asirk = Irk(loop, config)
    asirk.start()

    loop.run_until_complete(asirk.client_completed)


if __name__ == '__main__':
    main()
