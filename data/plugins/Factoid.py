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
import re
import os
import json

from core.plugin import Plugin


logger = logging.getLogger(__name__)


class Factoid(Plugin):
        def __init__(self, protocol):
            super().__init__(protocol)

            self.commands = {
                'fact': self.factoid,
            }

            self.admin_commands = {}
            
            # TODO: mysql DB
            self.dbfile = os.path.join(self.protocol.config['plugin_data_path'],
                                       'factDB')
            try:
                with open(self.dbfile, 'r') as f:
                    lines = ''.join([line for line in f.readlines()])
                    if len(lines):
                        self.db = json.loads(lines)
                    else:
                        self.db = []
            except IOError:
                self.db = []

        def msg_hook(self, event):
            # TODO: Standardize with commands + event API
            # + documented values for PRIVSMG / CMD
            sender = event.prefix[0]
            try:
                destination, message = event.params.split(' ', 1)
            except (IndexError, ValueError):
                return

            message = message[1:]

            # TODO: this should probably be a plugin utility function
            if sender == "NICKSERV" or event.cmd != "PRIVMSG" or \
               message[0] == self.protocol.bot.command_symbol or \
               message[0] == ':':
                return

            # Factoid Response
            # TODO: test for 90-95% similarity
            for inp, action, response in self.db:
                if inp in message:
                    self.protocol.respond(self.protocol.last_dest, response)

        def factoid(self, event):
            """<list>|<new|del> [fact|index]"""
            try:
                _, cmd, msg = event.msg.split(' ', 2)
            # TODO: FIX
            except (ValueError, IndexError):
                _, cmd = event.msg.split(' ', 1)
                msg = "<>"

            parameters = "<> {}".format(msg)
    
            if cmd == 'new':
                _, message = parameters.split(' ', 1)

                # New Factoid Creation
                # TODO: store by index, one input/many responses
                data = re.split("(.*) <(.*)> (.*)", message)
                if data[0] == '' and data[-1] == '':
                    _, inp, action, response, _ = data
                    self.db.append((inp, action, response))
                    m = "\'{} <{}> {}\' is now recorded.".format(inp,
                                                                 action,
                                                                 response)
                    self.protocol.respond(event.dest, m)

                    with open(self.dbfile, 'w+') as f:
                        f.writelines(json.dumps(self.db))
            # Generalize ownership API TODO
            elif cmd == 'del' and \
            self.protocol.config['owner'] == event.prefix[0]:
                _, message = event.msg.split(' ', 1)
                fact = self.db.pop(int(message))
                self.protocol.respond(event.dest,
                                      "Factoid \'{}\' deleted.".format(fact))
            elif cmd == 'list':
                self.protocol.respond(event.dest,
                                      [i for i in enumerate(self.db)])
