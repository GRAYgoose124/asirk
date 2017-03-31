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
import sys
import asyncio
import logging
import argparse 

# TODO: Fix debug
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s.%(msecs)03d [%(levelname)4s] %(name)10s:%(lineno)4s |%(message)s',
                    datefmt="%H%M:%S")
logger = logging.getLogger(__name__)

if os.name != 'nt':
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except:
        logger.warning(" Not using uvloop!")
else:
    logger.warning(" Not using uvloop!")

from core.bot import Irk
from core.config import load_config, save_config


def args():
    parser = argparse.ArgumentParser(description="asyncio irc bot.")
    results = parser.parse_args(*sys.argv)
    
def main():
    loop = asyncio.get_event_loop()

    # This is really just because I'm using pycharm on windows...
    if os.name != 'nt':
        home_path = os.path.join(os.getcwd(), 'asirk')
    else:
        home_path = os.getcwd()

    data_path = os.path.join(home_path, 'data')

    config_path = os.path.join(data_path, 'config.json')
    plugin_path = os.path.join(data_path, 'plugins')

    config = load_config(config_path)

    # asyncio Protocols requires b'host:port' format.    
    config['host'] = bytes(config['host'], 'utf-8')
    config['port'] = bytes(config['port'], 'utf-8')
    config['plugin_path'] = plugin_path
    config['plugin_data_path'] = os.path.join(plugin_path, 'data')

    asirk = Irk(loop, config)
    asirk.start()

    loop.run_until_complete(asirk.client_completed)


if __name__ == '__main__':
    main()
