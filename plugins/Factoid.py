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

from plugin import Plugin


logger = logging.getLogger(__name__)


class Factoid(Plugin):
        def __init__(self, protocol):
            super().__init__(protocol)

            self.commands = {
                'fact': self.new_factoid,
                'rmfact': self.delete_factoid
            }

            self.db = []
            self.db_path = None

        def privmsg_hook(self, prefix, command, parameters):
            pass

        def new_factoid(self, prefix, destination, message):
            self.protocol.send_response(destination, message)

        def delete_factoid(self, prefix, command, parameters):
            pass

