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

from core.plugin import Plugin

logger = logging.getLogger(__name__)

class Alias(Plugin):
    def __init__(self, protocol):
        super().__init__(protocol)

        self.alias_list = {'dice': 'help'}
        
        self.commands = { 'newalias': self.newalias,
                          'oldalias': self.oldalias
                          }
        
    # TODO: Functionalize command usage in bot.py 
    def msg_hook(self, prefix, command, parameters):
        channel, message = parameters.split(' ', 1)
        message = message[1:]
                
        if message[0] == self.protocol.bot.command_symbol:
            cmd, params = message, ' '

            try:
                cmd, params = message.split(' ', 1)
                cmd = cmd[1:]
            except:
                pass
                
            if cmd in self.alias_list:
                alias_msg = (prefix, command, "{} :.{} {}".format(channel, self.alias_list[cmd], params))

                self.protocol.bot.process(*alias_msg)
                
                logger.info("ALS| Alias found: {} -> {}".format(cmd, self.alias_list[cmd]))

    def newalias(self, prefix, command, parameters):
        pass        
        
    def oldalias(self, prefix, command, parameters):
        pass
