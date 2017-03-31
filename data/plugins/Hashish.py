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
import time
import logging
import hashlib
import os
import json

from core.plugin import Plugin
from core.irc import Irc


logger = logging.getLogger(__name__)


class Hashish(Plugin):
    def __init__(self, protocol):
        super().__init__(protocol)

        self.admin_commands = {'rehash': self.rehash_whois}
        self.commands = {'hash': self.hash_whois, 'login': self.login}

        self.digests_file = os.path.join(self.protocol.config['plugin_data_path'], "whois.digest")
        try:
            with open(self.digests_file, "r") as f:
                self.digests = json.loads(f.read())
        except (IOError, json.decoder.JSONDecodeError):
            self.digests = {}
        
        logger.info("MD5| {}".format(self.digests))
       
        self.caught_whois = {}
        self.whois_cmds = ['311', '312', '317', '318']
        
        self.last_hashed = None

    def msg_hook(self, *event):
        if event[1] in self.whois_cmds:
            logger.info("   | {}".format(event[1]))
            self.caught_whois[event[1]] = hashlib.md5(event[2].encode('ascii'))

        # RFC ENDOFWHOIS
        if event[1] == '318':
            digest = ""
            digest = ":".join(map(lambda x: x.hexdigest(), self.caught_whois.values()))
    
            if self.last_hashed is not None:
                if self.last_hashed in self.digests:
                    if self.digests[self.last_hashed] != digest:
                        self.protocol.send_response(self.protocol.last_dest, "New: {}, Changed Hash!".format(digest[::3]))
                        if self.last_hashed == self.protocol.config['owner']:
                            self.protocol.send_response(self.protocol.config['owner'], "Please Re-Auth")
                    else:
                        self.protocol.send_response(self.protocol.last_dest, "New: {}, Unchanged Hash.".format(digest[::3]))
                else:
                    self.digests[self.last_hashed] = digest
                    self.last_hashed = None
                    self.protocol.send_response(self.protocol.last_dest, "Set: {}, New Hash!".format(digest[::3]))
            else:
                logger.debug("Unrequested WHOIS: {}".format(digest))
                
            try:
                with open(self.digests_file, "w") as f:
                    f.write(json.dumps(self.digests))
            except IOError:
                logger.warning("DB cannot be saved!")
                       
    def hash_whois(self, *event):
        parameters = event[2].split(' ', 1)[1].split(' ') 
        self.protocol.send(Irc.whois(parameters[0]))        

        self.last_hashed = parameters[0]
        
        if self.last_hashed in self.digests:
            self.protocol.send_response(event[1], "Stored MD5: {}: {}".format(event[0][0], self.digests[self.last_hashed][::3]))
    
    def login(self, *event):
        # TODO: Essentially password-protected query to rehash. Will require some bot restructure.
        pass

    def rehash_whois(self, *event):
        hashed = event[2].split(' ', 1)[1].split(' ')[0]
        try:
            del(self.digests[hashed])
        except (KeyError, IndexError): 
            pass
            
        self.hash_whois(*event)
