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
import time
import logging

from lib.plugin import Plugin
from lib.irc import Irc


logger = logging.getLogger(__name__)


class StrCMD(Plugin):
    def __init__(self, protocol):
        super().__init__(protocol)

        self.commands = {
            'struct': self.struct
        }

    def struct(self, *event):
        """-> A simple structured command."""
        print("test")
    
    def _sub1():
        pass
    
    def _sub2():
        pass
        
    def _sub2_sub1():
        pass
