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

from lib.plugin import Plugin
from lib.irc import Irc


logger = logging.getLogger(__name__)


class IrcUtils(Plugin):
    def __init__(self, protocol):
        super().__init__(protocol)

        self.commands = {
            'ping': self.ping,
            'joined': self.joined,
        }

        self.admin_commands = {
            'join': self.join,
            'part': self.part,
        }

    def ping(self, prefix, destination, parameters):
        """<user> -> bot pings to <user>."""
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

    def join(self, prefix, destination, parameters):
        """<channel> -> bot joins <channel>."""
        channel = parameters.split(' ')[1]

        self.protocol.send(Irc.join(channel))
        self.protocol.send_response(destination, "Joining: {}".format(channel))

    def part(self, prefix, destination, parameters):
        """<channel> -> bot parts <channel>."""
        channel = parameters.split(' ')[1]
        self.protocol.send(Irc.part(channel))
        self.protocol.send_response(destination, "Parted: {}".format(channel))

    def joined(self, prefix, destination, parameters):
        self.protocol.send_response(destination, "Channels: {}".format(list(self.protocol.users.keys())))
