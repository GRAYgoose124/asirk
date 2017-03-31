#   asIrk: asyncio irc bot
#   Copyright (C) 2016  Grayson Miller
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
import time
import inspect
import os
import atexit
import sys

from core.plugin import Plugin
from core.irc import Irc


logger = logging.getLogger(__name__)


GIT_SOURCE = "https://github.com/GRAYgoose124/asirk"


class BotUtils(Plugin):
    def __init__(self, protocol):
        super().__init__(protocol)

        self.commands = {
            'echo': self.echo,
            'uptime': self.uptime,
            'help': self.help,
            'docs': self.mysource
        }

        self.admin_commands = {
            'bound': self.bound,
            'rawecho': self.rawecho,
            'conf': self.config,
            'restart': self.restart,
            'quit': self.quit
        }

    def rawecho(self, prefix, destination, message):
        self.protocol.send(' '.join(message.split(' ')[1:]))

    def echo(self, prefix, destination, message):
        """<message> -> bot: <message>"""
        if destination == self.protocol.config['nick']:
            destination = prefix[0]

        self.protocol.send_response(destination, ' '.join(message.split(' ')[1:]))

    def mysource(self, prefix, destination, parameters):
        """-> returns git url."""
        self.protocol.send_response(destination, "My most recently published source can be found here: {}".format(GIT_SOURCE))

    def uptime(self, prefix, destination, parameters):
        """-> returns the average process time and uptime of the bot."""
        up = (time.time() - self.protocol.starttime) / 60
        self.protocol.send_response(destination, "Uptime: {:.2f} minutes.".format(up))

    def config(self, prefix, destination, parameters):
        self.protocol.send_notice(prefix[0], "config: {}".format(self.protocol.config))

    def quit(self, prefix, destination, parameters):
        self.protocol.bot.stop()

    def restart(self, prefix, destination, parameters):
        def __restart():
            python = sys.executable
            os.execl(python, python, *sys.argv)
            
        atexit.register(__restart)
        self.protocol.bot.stop()

    def bound(self, prefix, destination, parameters):
        """<command> -> What plugin that command comes from"""
        _, bound_cmd, *_ = parameters.split(' ', 2)
            
        message = "Invalid command."
    
        acl = self.protocol.bot.admin_commands.copy()
        command_list = dict(self.protocol.bot.commands, **acl)
    
        if bound_cmd == 'all':
            d = {}
            for n, c in command_list.items():
                cn = str(c.__self__.__class__).split("\'")[1]
                cn = cn.split(".")[1]
         
                if cn not in d:      
                    d[cn] = [n]
                else:
                    d[cn].append(n)            
            
            message = str(d).translate({ord(k): v for k, v in {',': None, '{': None, '}': None, '[': None, ']': '\r\n', '\'': None}.items()})
            messages = message.split('\r\n')
            try:
                for m in messages:
                    if m[0] == ' ':
                        m = m[1:]
                    self.protocol.send_response(destination, m)
            except IndexError:
                pass
        else:
            try:
                message = command_list[bound_cmd].__self__.__class__
            except KeyError:
                pass

            message = "Command \'{}\' from \'{}\'".format(bound_cmd, str(message).split("\'")[1].split(".")[1])
                            
            self.protocol.send_response(destination, message)

    def help(self, prefix, destination, parameters):
        """<command> -> extra information on using <command>."""
        cmds = []

        try:
            help_cmd = parameters.split(' ')[1]
            
            if help_cmd == 'all':
                for cmd in self.protocol.bot.admin_commands:
                    self._single_help(cmd, destination) 
                for cmd in self.protocol.bot.commands:
                    self._single_help(cmd, destination)
            else:
                self._single_help(help_cmd, destination)
        except IndexError:
            cmds += ["{}*".format(cmd) for cmd in self.protocol.bot.admin_commands]
            cmds += [cmd for cmd in self.protocol.bot.commands]
            
            self.protocol.send_response(destination, ", ".join(cmds))

    def _single_help(self, help_cmd, destination):
            try:
                for line in self.protocol.bot.commands[help_cmd].__doc__.split('\n'):
                    self.protocol.send_response(destination, "{} {}".format(help_cmd, line)) 
                    return 
            except:
                pass
            try:
                for line in self.protocol.bot.admin_commands[help_cmd].__doc__.split('\n'):
                    self.protocol.send_response(destination, "{} {}".format(help_cmd, line))
                return
            except:
                pass

