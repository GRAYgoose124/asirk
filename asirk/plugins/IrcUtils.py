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
import time

from asirk.core.plugin import Plugin
from asirk.core.irc import Irc


logger = logging.getLogger(__name__)


class IrcUtils(Plugin):
    def __init__(self, protocol):
        super().__init__(protocol)

        self.commands = {
            "ping": self.ping,
            "joined": self.joined,
        }

        self.admin_commands = {
            "join": self.join,
            "part": self.part,
            "rawecho": self.rawecho,
        }

    def msg_hook(self, event):
        pass

    def rawecho(self, event):
        self.protocol.send(" ".join(event.msg.split(" ")[1:]))

    def ping(self, event):
        """<user> -> bot pings to <user>."""
        try:
            user = event.msg.split(" ")[1]
        except IndexError:
            self.protocol.respond(event.dest, "Incorrect ping command.")
            return

        if user == self.protocol.config["nick"]:
            self.protocol.respond(event.dest, "THE FUCK YOU PING YOURSELF?")
            return

        unix_timestamp = str(time.time()).replace(".", " ")
        self.protocol.send(Irc.ctcp_ping(user, unix_timestamp))
        logger.info("PNG| {}".format(user))

    def join(self, event):
        """<channel> -> bot joins <channel>."""
        channel = event.msg.split(" ")[1]

        self.protocol.send(Irc.join(channel))
        self.protocol.respond(event.dest, "Joining: {}".format(channel))

    def part(self, event):
        """<channel> -> bot parts <channel>."""
        channel = event.msg.split(" ")[1]
        self.protocol.send(Irc.part(channel))
        self.protocol.respond(event.dest, "Parted: {}".format(channel))

    def joined(self, event):
        self.protocol.respond(
            event.dest, "Channels: {}".format(list(self.protocol.users.keys()))
        )
