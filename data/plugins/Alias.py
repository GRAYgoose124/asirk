# TODO: Fix all plugin headders.
#   Alias: aliasing plugin for asIrk
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

        self.aliases = {'dice': 'help'}
        
        self.commands = {'newalias': self.newalias,
                         'oldalias': self.oldalias}
        
    # TODO: Functionalize command usage in bot.py 
    def msg_hook(self, event):
        try:
            channel, message = event.params.split(' ', 1)
            message = message[1:]
        except (ValueError, IndexError):
            return

        if message[0] == self.protocol.bot.command_symbol:
            cmd, params = message, ''

            try:
                cmd, params = message.split(' ', 1)
            except (ValueError, IndexError):
                params = ''

            cmd = cmd[1:]

            logger.debug('ALS| Seeking alias: {}'.format(cmd))

            if cmd in self.aliases:
                alias_msg = (tuple(event.prefix), "PRIVMSG",
                             "{} :.{} {}".format(channel, self.aliases[cmd],
                                                 params))

                logger.info("ALS| {}".format(alias_msg))

                # TODO: split process so you can hook into a bot API side.
                self.protocol.bot.process(*alias_msg)

                msg = "ALS| Alias found: {} -> {}".format(cmd,
                                                          self.aliases[cmd])
                logger.info(msg)

    def newalias(self, event):
        pass        
        
    def oldalias(self, event):
        pass
