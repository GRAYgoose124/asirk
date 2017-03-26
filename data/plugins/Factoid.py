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
import os
import json

from lib.plugin import Plugin


logger = logging.getLogger(__name__)


class Factoid(Plugin):
        def __init__(self, protocol):
            super().__init__(protocol)

            self.commands = {
                'fact': self.factoid,
            }

            self.admin_commands = {
                }
            
            # TODO: mysql DB
            self.db_file = os.path.join(self.protocol.config['plugin_data_path'], 'factDB')
            try:
                with open(self.db_file, 'r') as f:
                    lines = ''.join([line for line in f.readlines()])
                    if len(lines):
                        self.db = json.loads(lines)
                    else:
                        self.db = []
            except IOError:
                self.db = []

        def msg_hook(self, prefix, command, parameters):
            # TODO: Standardize with commands + event API + documented values for PRIVSMG / CMD
            sender = prefix[0]
            destination, message = parameters.split(' ', 1)
            message = message[1:]

            # Stop on command this is a hack.
            if message[0] == self.protocol.bot.command_symbol or message[0] == ':':
                return

            # Factoid Response
            # TODO: test for 90-95% similarity
            for input, action, response in self.db:
                # TODO make command API
                if destination == self.protocol.config['nick']:
                    destination = prefix[0]
                    
                if input in message:
                    self.protocol.send_response(destination, response)


        # TODO: Need to document event* API
        def add_factoid(self, prefix, destination, parameters):
            _, message = parameters.split(' ', 1)

            # New Factoid Creation
            # TODO: store by index, one input/many responses
            data = re.split("(.*) <(.*)> (.*)", message)
            if data[0] == '' and data[-1] == '':
                _, input, action, response, _ = data
                self.db.append((input, action, response))
                self.protocol.send_response(destination, "\'{} <{}> {}\' is now recorded.".format(input, action, response))
            
            with open(self.db_file, 'w+') as f:
               f.writelines(json.dumps(self.db))

        def list_factoids(self, prefix, destination, parameters):
            self.protocol.send_response(destination, [i for i in enumerate(self.db)])

        def delete_factoid(self, prefix, destination, parameters):
            _, message = parameters.split(' ', 1)
            fact = self.db.pop(int(message))
            self.protocol.send_response(destination, "Factoid \'{}\' deleted.".format(fact))

        def factoid(self, prefix, destination, parameters):
            """<list>|<new|del> [fact|index]"""
            try:
                _, cmd, params = parameters.split(' ', 2)
            # TODO: FIX
            except Exception:
                _, cmd = parameters.split(' ', 1)
                params = "<>"
                
            parameters = "<> {}".format(params)
    
            print(parameters)            
            if cmd == 'new':
                self.add_factoid(prefix, destination, parameters)
            # Generalize ownership API TODO
            elif cmd == 'del' and self.protocol.config['owner'] == prefix[0]:
                self.delete_factoid(prefix, destination, parameters)
            elif cmd == 'list':
                self.list_factoids(prefix, destination, parameters)
