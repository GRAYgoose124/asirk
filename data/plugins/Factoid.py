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
import re

from plugin import Plugin


logger = logging.getLogger(__name__)


class Factoid(Plugin):
        def __init__(self, protocol):
            super().__init__(protocol)

            self.admin_commands = {
                'rmfact': self.delete_factoid
            }
            
            # TODO: mysql DB
            self.db = []

        def privmsg_hook(self, prefix, command, parameters):
            # TODO: Standardize with commands + event API + documented values for PRIVSMG / CMD
            sender = prefix[0]
            destination, message = parameters.split(' ', 1)
            message = message[1:]

            # Factoid Response
            # TODO: test for 90-95% similarity
            for input, action, response in self.db:
                if input in message:
                    self.protocol.send_response(destination, response)

            # New Factoid Creation
            # TODO: store by index, one input/many responses
            data = re.split("(.*) <(.*)> (.*)", message)
            if data[0] == '' and data[-1] == '':
                _, input, action, response, _ = data
                self.db.append((input, action, response))
                self.protocol.send_response(destination, "\'{} <{}> {}\' is now recorded.".format(input, action, response))

        def list_factoids(self, prefix, command, parameters):
            pass

        def delete_factoid(self, prefix, command, parameters):
            pass
