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

from plugin import Plugin


logger = logging.getLogger(__name__)


class BotUtils(Plugin):
    def __init__(self, protocol):
        super().__init__(protocol)

        self.commands = {
            'echo': self.echo,
            'ping': self.ping
        }

        self.admin_commands = {
            'rawecho': self.rawecho
        }

        self.db = []
        self.db_path = None

    def privmsg_hook(self, prefix, command, parameters):
        pass

    def rawecho(self, prefix, destination, message):
        self.protocol.send(' '.join(message.split(' ')[1:]))  

    def echo(self, prefix, destination, message):
        if destination == self.protocol.config['nick']:
            destination = self.commander

        self.protocol.send_response(destination, ' '.join(message.split(' ')[1:]))            

    def ping(self, prefix, destination, parameters):
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

