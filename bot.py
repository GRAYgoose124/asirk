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
import os
import sys
import atexit
import traceback

from irc import Irc, IrcProtocol
from plugin import PluginManager


logger = logging.getLogger(__name__)


class Irk(PluginManager):
    def __init__(self, loop, config):
        super().__init__(None, config['plugin_path'])
        self.client_completed = asyncio.Future()

        self.loop = loop
        self.config = config

        self.elapsed = 0

        self.client = None
        self.transport, self.protocol = None, None

        self.command_symbol = '.'
        self.commander = None
    
        self.admin_commands.update({'quit': self._cmd_quit,
                                    'restart': self._cmd_restart,
                                    'plugin': self._cmd_plugin
                                    })


    def start(self):
        self.client = self.loop.create_connection(functools.partial(IrcProtocol,
                                                                    future=self.client_completed,
                                                                    config=self.config),
                                                  self.config['host'],
                                                  self.config['port'],
                                                  ssl=self.config['ssl'])

        self.transport, self.protocol = self.loop.run_until_complete(self.client)

        self.protocol.starttime = time.time()
        
        self.protocol.set_callback(self.process)
        # TODO: This shouldn't be necessary but for compatibility.... so API 
        # to self.bot.etc and self.protocol.etc
        self.protocol.set_bot(self)

        self.load_plugins()
        logger.info(" P | Loaded plugins: {}".format(list(self.plugins.keys())))

    def stop(self):
        self.protocol.send(Irc.quit("Stopping..."))
        self.transport.close()

        self.client = None
        self.transport, self.protocol = None, None

    # Bot
    def process(self, prefix, command, parameters):
        user, ident, host = prefix

        start = time.clock()

        if command == 'PRIVMSG':
            self.commander = user
            destination, message = Irc.split_privmsg(parameters)

            if destination == self.config['nick']:
                destination = user

            for name, plugin in self.plugins.items():
                try:
                    #:TODO catch plugin exceptions so that they won't break the bot.
                    plugin.privmsg_hook(prefix, command, parameters)
                except NotImplementedError:
                    pass
                except Exception as e:
                    logger.warn("ERR| PRIVMSG hook!")
                    traceback.print_tb(e.__traceback__)

            bot_cmd = message.split(' ')[0]
            if self.command_symbol == bot_cmd[0]:
                bot_cmd = bot_cmd[1:]

                try:
                    # TODO: API API API
                    # TODO: Better admin authentication, multiuser
                    # TODO: multinetwork
                    if self.commander == self.config['owner']:
                        for k, v in self.admin_commands.items():
                            if bot_cmd == k:
                                v(prefix, destination, message)
                                break
                    for k, v in self.commands.items():
                        if bot_cmd == k:
                            v(prefix, destination, message)
                            break
                except Exception as e:
                    logger.warn("ERR| Plugin command!")
                    traceback.print_tb(e.__traceback__)

            elif command == 'NOTICE':
                pass

        elif command == '401':
            self.protocol.send_response(self.protocol.last_dest, "That nick is invalid.")

        if self.elapsed == 0:
            average_div = 1.0
        else:
            average_div = 2.0

        self.elapsed += time.clock() - start
        self.elapsed = self.elapsed / average_div

        logger.debug("TIM| bot processing time: avg. {:.3f} ms".format(self.elapsed))

    # quit, restart + help in plugins
    def _cmd_quit(self, prefix, destination, parameters):
        self.stop()

    # TODO: document parameters api then wrap in *event
    def _cmd_restart(self, prefix, destination, parameters):
        def __restart():
            python = sys.executable
            os.execl(python, python, *sys.argv)

        atexit.register(__restart)
        self.stop()
        
    def _cmd_plugin(self, prefix, destination, parameters):
        """plugin <loaded|list>|<unload|load|reload> [name|all]"""
        plugin_cmd = parameters.split(' ')[1]

        if plugin_cmd == 'loaded':
            self.protocol.send_response(destination, "Loaded plugins: {}".format([i for i in self.plugins.keys()]))

        elif plugin_cmd == 'unload':
            plugin_name = parameters.split(' ')[2]

            if plugin_name == "all":
                self.unload_plugins()
                self.protocol.send_response(destination, "All plugins unloaded.")
            elif plugin_name in self.plugins:
                self.unload_plugin(plugin_name)
                self.protocol.send_response(destination, "Plugin {} unloaded.".format(plugin_name))

        elif plugin_cmd == 'load':
            plugin_name = parameters.split(' ')[2]

            if plugin_name == "all":
                self.load_plugins()
                self.protocol.send_response(destination, "All plugins loaded: {}".format([i for i in self.plugins.keys()]))
            elif self.load_plugin(plugin_name) is not None:
                self.protocol.send_response(destination, "Plugin {} loaded.".format(plugin_name))
            else:
                self.protocol.send_response(destination, "Invalid plugin to load.")

        elif plugin_cmd == 'reload':
            plugin_name = parameters.split(' ')[2]

            if plugin_name == "all":
                self._cmd_plugin(prefix, destination, '<> unload all')
                self._cmd_plugin(prefix, destination, '<> load all')
            elif plugin_name in self.plugins:
                # TODO: Fix this...derp...
                self._cmd_plugin(prefix, destination, '<> unload {}'.format(plugin_name))
                self._cmd_plugin(prefix, destination, '<> load {}'.format(plugin_name))
            else:
                self.protocol.send_response(destination, "Invalid plugin to reload.")

        elif plugin_cmd == 'list':
            plugs = [i for i in self.list_plugins()]
            self.protocol.send_response(destination, "{}".format(plugs))

            # TODO: Plugin error responses, catch the splits exceptions

