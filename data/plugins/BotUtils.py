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

from plugin import Plugin
from irc import Irc


logger = logging.getLogger(__name__)


class BotUtils(Plugin):
    def __init__(self, protocol):
        super().__init__(protocol)

        self.commands = {
            'echo': self.echo,
            'ping': self.ping,
            'uptime': self.uptime,
            'joined': self.joined,
            'help': self.help
        }

        self.admin_commands = {
            'bound': self.bound,
            'rawecho': self.rawecho,
            'join': self.join,
            'part': self.part,
            'conf': self.config
        }

    def rawecho(self, prefix, destination, message):
        self.protocol.send(' '.join(message.split(' ')[1:]))

    def echo(self, prefix, destination, message):
        """echo <message> -> bot: <message>"""
        if destination == self.protocol.config['nick']:
            destination = prefix[0]

        self.protocol.send_response(destination, ' '.join(message.split(' ')[1:]))

    def ping(self, prefix, destination, parameters):
        """ping <user> -> bot pings to <user>."""
        try:
            user = parameters.split(' ')[1]
        except IndexError:
            self.protocol.send_response(destination, "Incorrect ping command.")
            return

        if user == self.protocol.config['nick']:
            self.protocol.send_response(destination, "THE FUCK YOU PING YOURSELF?")
            return

        unix_timestamp = str(time.time()).replace(".", " ")
        self.protocol.send(Irc.ctcp_ping(user, unix_timestamp))
        logger.info("PNG| {}".format(user))

    def uptime(self, prefix, destination, parameters):
        """uptime -> returns the average process time and uptime of the bot."""
        self.protocol.send_response(destination, "Average process time: {:.4f}ms".format(self.protocol.elapsed))
        self.protocol.send_response(destination, "Uptime: {:.2f} seconds.".format(time.time() - self.protocol.starttime))

    def join(self, prefix, destination, parameters):
        """join <channel> -> bot joins <channel>."""
        channel = parameters.split(' ')[1]

        self.protocol.send(Irc.join(channel))
        self.protocol.send_response(destination, "Joining: {}".format(channel))

    def part(self, prefix, destination, parameters):
        """part <channel> -> bot parts <channel>."""
        channel = parameters.split(' ')[1]
        self.protocol.send(Irc.part(channel))
        self.protocol.send_response(destination, "Parted: {}".format(channel))

    def joined(self, prefix, destination, parameters):
        self.protocol.send_response(destination, "Channels: {}".format(self.protocol.users))
        
    def config(self, prefix, destination, parameters):
        self.protocol.send_notice(prefix[0], "config: {}".format(self.protocol.config))

    def bound(self, prefix, destination, parameters):
        """bound <command> -> What plugin that command comes from"""
        bound_cmd = parameters.split(' ')[1]
        message = "Invalid command."
   
        try:
            message = self.protocol.bot.commands[bound_cmd].__self__.__class__
        except:
            pass
   
        try:
            message = self.protocol.bot.admin_commands[bound_cmd].__self__.__class__
        except:
            pass

        self.protocol.send_response(destination, message)

    def help(self, prefix, destination, parameters):
        """help <command> -> extra information on using <command>."""
        cmds = []

        try:
            help_cmd = parameters.split(' ')[1]
            try:
                for line in self.protocol.bot.commands[help_cmd].__doc__.split('\n'):
                    self.protocol.send_response(destination, line)
                return
            except:
                pass
            try:
                for line in self.protocol.bot.admin_commands[help_cmd].__doc__.split('\n'):
                    self.protocol.send_response(destination, line)
                return
            except:
                pass
        except:
            if prefix[0] == self.protocol.config['owner']:
                cmds += [cmd for cmd in self.protocol.bot.admin_commands]
            cmds += [cmd for cmd in self.protocol.bot.commands]
            
            self.protocol.send_response(destination, cmds)
