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


class IrcBot(PluginManager):
    def __init__(self, loop, config):
        super().__init__(None, config['plugin_path'])
        self.client_completed = asyncio.Future()

        self.loop = loop
        self.config = config

        self.client = None
        self.transport, self.protocol = None, None

        self.commander = None

    def start(self):
        self.client = self.loop.create_connection(functools.partial(IrcProtocol,
                                                                    future=self.client_completed,
                                                                    config=self.config),
                                                  self.config['host'],
                                                  self.config['port'],
                                                  ssl=self.config['ssl'])

        self.transport, self.protocol = self.loop.run_until_complete(self.client)
        self.protocol.set_callback(self.process)

        self.load_plugins()

    def stop(self):
        self.protocol.send(Irc.quit("Stopping..."))
        self.transport.close()

        self.client = None
        self.transport, self.protocol = None, None

    # IrcProtocol message callback
    def process(self, prefix, command, parameters):
        raise NotImplementedError


class Irk(IrcBot):
    def __init__(self, loop, config):
        super().__init__(loop, config)

        self.admin_commands.update({'quit': self._cmd_quit,
                                    'restart': self._cmd_restart,
                                    'plugin': self._cmd_plugin,
                                    })

        self.commands.update({'help': self._cmd_help
                              })

        self.command_symbol = '.'
        self.commander = None


        self.elapsed = 0

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
                    logger.debug(e)

            bot_cmd = message.split(' ')[0]
            if self.command_symbol == bot_cmd[0]:
                bot_cmd = bot_cmd[1:]

                try:
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
                    traceback.print_exc(e)
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

    def _cmd_quit(self, prefix, destination, parameters):
        self.stop()

    # TODO: document parameters api then wrap in *event
    def _cmd_restart(self, prefix, destination, parameters):
        def __restart():
            python = sys.executable
            os.execl(python, python, *sys.argv)

        atexit.register(__restart)
        self.stop()

    def _cmd_help(self, prefix, destination, parameters):
        cmds = {'user': [cmd for cmd in self.commands],
                'admin': [cmd for cmd in self.admin_commands]}

        self.protocol.send_response(destination, cmds)

    def _cmd_plugin(self, prefix, destination, parameters):
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
                self.protocol.send_response(destination, "Invalid plugin.")

        elif plugin_cmd == 'reload':
            plugin_name = parameters.split(' ')[2]

            if plugin_name == "all":
                self.unload_plugins()
                self.load_plugins()
                self.protocol.send_response(destination, "All plugins reloaded.")
            elif plugin_name in self.plugins:
                # TODO: Fix this...derp...
                self._plugin_unload(prefix, destination, parameters)
                self._plugin_load(prefix, destination, parameters)
    # TODO: Plugin error responses, catch the splits exceptions

