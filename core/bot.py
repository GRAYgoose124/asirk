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
import functools
import time
import traceback
from collections import namedtuple

from .irc import Irc, IrcProtocol
from .plugin import PluginManager


logger = logging.getLogger(__name__)


# API helpers
IrcEvent = namedtuple('IrcEvent', 'prefix cmd params')
BotEvent = namedtuple('BotEvent', 'user dest msg')


# TODO: Rename to Bot
class Irk(PluginManager):
    def __init__(self, loop, config):
        super().__init__(None, config['plugin_path'])
        self.client_completed = asyncio.Future()

        self.loop = loop
        self.config = config

        self.client = None
        self.transport, self.protocol = None, None

        self.command_symbol = '.'
        self.commander = None
    
        self.admin_commands.update({'plugin': self.__cmd_plugin})

    def start(self):
        logger.info(" O | Starting...")
        prot = functools.partial(IrcProtocol, future=self.client_completed,
                                 config=self.config)

        self.client = self.loop.create_connection(prot, self.config['host'],
                                                  self.config['port'],
                                                  ssl=self.config['ssl'])

        self.transport, self.protocol = \
        self.loop.run_until_complete(self.client)

        self.protocol.starttime = time.time()
        
        self.protocol.set_callback(self.process)
        # TODO: This shouldn't be necessary but hack...
        self.protocol.set_bot(self)

        self.load_plugins()
        plugs = list(self.plugins.keys())
        logger.info(" P | Loaded plugins: {}: {}".format(plugs, len(plugs)))

    def stop(self):
        logger.info(" X | Stopping...")
        self.protocol.send(Irc.quit("Stopping..."))
        self.transport.close()

        self.client = None
        self.transport, self.protocol = None, None

    # Bot
    def process(self, prefix, command, parameters):
        user, ident, host = prefix

        for name, plugin in self.plugins.items():
            try:
                # TODO: async dispatch
                plugin.msg_hook(IrcEvent(prefix, command, parameters))
            except NotImplementedError:
                pass
            except Exception as e:
                msg = "ERR| PRIVMSG hook! {}\n{}: {}"
                logger.warning(msg.format(name, e.__class__.__name__, e))
                traceback.print_tb(e.__traceback__)

        if command == 'PRIVMSG':
            self.commander = user
            destination, message = Irc.split_privmsg(parameters)

            if destination == self.config['nick']:
                destination = user

            bot_cmd = message.split(' ')[0]
            if len(bot_cmd) == 0:
                return
                
            if self.command_symbol == bot_cmd[0]:
                logger.debug("CMD| Trying {}".format(bot_cmd))
                bot_cmd = bot_cmd[1:]

                try:
                    # TODO: Better admin authentication,
                    # TODO: multiuser, multinetwork
                    if self.commander == self.config['owner']:
                        for k, v in self.admin_commands.items():
                            if bot_cmd == k:
                                v(BotEvent(user, destination, message))
                                break
                    for k, v in self.commands.items():
                        if bot_cmd == k:
                            v(BotEvent(user, destination, message))
                            break
                except Exception as e:
                    msg = "EXC| {} in plugin command!\n  -> {}\n\tmessage: {}"
                    logger.warning(msg.format(e.__class__.__name__,
                                              e, parameters))
                    traceback.print_tb(e.__traceback__)
        elif command == 'NOTICE':
            logger.debug(" ? | Caught a notice? {}".format(parameters))
        elif command == '401':
            self.protocol.respond(self.protocol.last_dest,
                                  "That nick is invalid.")
        elif command == '311':
            pass
        else:
            logger.debug(" ? | Uncaught: {}".format(command))

    # TODO: Move to hardcoded autoloaded plugin?
    def __cmd_plugin(self, event):
        """<list>|<unload|load> [name|all] -> Modify bot's plugins."""

        # TODO: Plugin structured cmd API, but at bot or plugin level?
        # TODO: have hooks return message and internally send?
        # Commands only use send_response once?
        try:
            _, plugin_cmd, plugin_name = event.msg.split(' ')
        except ValueError:
            plugin_name = None
            _, plugin_cmd = event.msg.split(' ')

        logger.info("PLG| {}".format(plugin_cmd))

        msg = None
        if plugin_cmd == 'list':
            msg = "Plugins: "
            loaded_plugs = self.plugins.keys()
            for plug in self.list_plugins():
                plug = plug[:-3]
                if plug in loaded_plugs:
                    msg += "*"
                msg += "{}, ".format(plug)
            msg += "loaded: {}.".format(len(loaded_plugs))
        elif plugin_cmd == 'unload':
            if plugin_name == "all":
                self.unload_plugins()
                msg = "All plugins unloaded."
            elif plugin_name in self.plugins:
                self.unload_plugin(plugin_name)
                msg = "Plugin {} unloaded.".format(plugin_name)
        elif plugin_cmd == 'load':
            if plugin_name == "all":
                self.load_plugins()
                msg = "Plugins loaded: {}".format(list(self.plugins.keys()))
            elif self.load_plugin(plugin_name) is not None:
                msg = "Plugin {} loaded.".format(plugin_name)
            else:
                msg = "Invalid plugin to load: {}.".format(plugin_name)

        if msg is not None:
            self.protocol.respond(event.dest, msg)
