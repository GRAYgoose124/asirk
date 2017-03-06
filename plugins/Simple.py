#   Irk: irc bot
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


class Simple(Plugin):
    def __init__(self, protocol):
        super().__init__(protocol)

        self.commands = {
            'test': self.test
        }

    def msg_hook(self, prefix, command, parameters):
        logger.info("Simple Hook")

    def test(self, prefix, command, parameters):
        logger.info("Simple Command")
