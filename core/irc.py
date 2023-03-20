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
import asyncio
import time
import re

logger = logging.getLogger(__name__)


default_client_config = {
    'host': '', 'port': 6667, 'ssl': False,
    'nick': '', 'pass': '',
    'ident': '', 'user': '',
    'mode': '+B', 'unused': '*',
    'owner': '', 'owner_email': ''
}


class IrcProtocol(asyncio.Protocol):
    def __init__(self, future, config=default_client_config):
        self.f = future
        self.message_buffer = ""

        self.config = config

        self.users = {}
        self.channels = []

        self.bot = None
        self.callback = lambda x, y, z: None
        self.last_dest = None
        self.transport = None
        self.send_buffer = ""
        self.elapsed = 0 
        
        self.irc_events = {
            'PRIVMSG': self._handle_privmsg,
            'NOTICE': self._handle_notice,
            'JOIN': self._handle_join,
            'PART': self._handle_part,
            '001': [self._handle_identify, self._set_mode],
            '332': self._qno_handle,
            '353': self._handle_userlist_update,
            '366': self._qno_handle,
            '376': self._handle_mode,
            '401': self._no_such_nick,
            '403': self._no_such_chan,
            '433': self._handle_433,
            'PING': self._handle_server_ping,
        }

    # Protocol Events
    def connection_made(self, transport):
        logger.debug("CON| {}".format(transport.get_extra_info('peername')))
        self.transport = transport

        self.send(Irc.nick(self.config['nick']))
        self.send(Irc.user(self.config['user'], self.config['unused'],
                           self.config['owner']))

    def data_received(self, data):
        data = data.decode('utf-8')
        
        self.message_buffer += data

        messages = self.message_buffer.split('\r\n')
        prepend_buffer = ""

        if self.message_buffer[-2:] != '\r\n':
            prepend_buffer = messages[-1]
            messages = messages[:-1]

        for message in messages:
            if len(message) != 0:
                # TODO: *event API 
                prefix, command, parameters = Irc.split_message(message)
                prefix = Irc.split_prefix(prefix)

                logger.info("-->| {}".format(message))

                irc_callback = self.irc_events.get(command, self._no_handle)
                if isinstance(irc_callback, list):
                    for cb in irc_callback:
                        cb(message)
                else:
                    irc_callback(message)

                self.callback(prefix, command, parameters)

        self.message_buffer = prepend_buffer

    def connection_lost(self, exc):
        logger.debug("END| Connection closed.")
        self.f.set_result(True)

    # Utility functions
    # TODO: add more irc_helpers
    def send(self, irc_msg):
        logger.info("<--| {}".format(irc_msg))

        self.send_buffer += "{}\r\n".format(irc_msg)
        self.transport.write(bytes("{}\r\n".format(irc_msg), encoding='utf-8'))

    # TODO: Move to Irk?

    def respond(self, dest, message):
        if dest is None:
            return

        # TODO: generalize message splitting and keep in Irc
        if len(message) > Irc.msg_size:
            n_msgs = int(len(message) / Irc.msg_size)
            for i in range(n_msgs+1):
                frame = message[Irc.msg_size*i:Irc.msg_size*(i+1)]
                self.send(Irc.privmsg(dest, frame))
        else:
            self.send(Irc.privmsg(dest, message))

    def send_notice(self, dest, message):
        if dest is None:
            return
        
        self.send(Irc.notice(dest, message))

    def set_callback(self, func):
        self.callback = func

    # TODO: Remove this: irc shouldn't need to know about bot.
    # (Plugin API hack atm)
    def set_bot(self, bot):
        self.bot = bot

    # IRC handlers
    @staticmethod
    def _qno_handle(message):
        pass

    @staticmethod
    def _no_handle(message):
        _, command, _ = Irc.split_message(message)
        logger.log(level=5, msg="Unknown IRC command: {}".format(command))

    def _handle_privmsg(self, message):
        prefix, command, parameters = Irc.split_message(message)
        sender, user, ident = Irc.split_prefix(prefix)

        channel, msg = parameters.split(" ", 1)

        if channel != self.config['nick']:
            self.last_dest = channel
        else:
            self.last_dest = sender

        if prefix is None:
            logger.debug("Malformed PRIVMSG: %s", message)
            return

        tokens = parameters.split(' ')
        
        try:
            if tokens[2] == '':
                return
        except IndexError:
            return
            
        # Handles the case of ": <text>". Someone started their message
        # with a space.
        if tokens[1] == ':':
            privmsg_command = tokens[2]
            message = "{} {}".format(privmsg_command, " ".join(tokens[2:]))
        else:
            privmsg_command = tokens[1][1:]
            message = "{} {}".format(privmsg_command, " ".join(tokens[2:]))

        # CTCP PRIVMSGs
        if privmsg_command == '\x01PING':
            self.send(Irc.ctcp_pong(sender, message.split(' ')[1]))
        elif privmsg_command == '\x01ACTION':
            pass
        elif privmsg_command[0] == '\x01':
            logger.debug('Missing CTCP command %s', privmsg_command)

    def _handle_identify(self, message):
        if self.config['nick'] != '' and self.config['nick'][0] != '_':
            self.send(Irc.identify(self.config['pass']))

    def _handle_notice(self, message):
        # CTCP PONG
        if message.split(" ")[3] == ":\x01PING":
            time_stamp = ".".join(message.split(" ")[-2:])[:-1]
            time_taken = round(time.time() - float(time_stamp[:-1]), 2)
            prefix, command, parameters = Irc.split_message(message)

            logger.info("PNG| response: {}".format(time_taken))
            self.respond(self.last_dest, "Time taken: {}".format(time_taken))

    @staticmethod
    def _no_such_nick(message):
        pass

    @staticmethod
    def _no_such_chan(message):
        pass

    def _set_mode(self, message):
        self.send(Irc.mode(self.config['nick'], self.config['mode']))

    def _handle_userlist_update(self, message):
        prefix, command, parameters = Irc.split_message(message)
        split_params = parameters.split(' ')
        users = split_params[3:][:-1]

        channel = split_params[2]
        if len(users) == 0:
            self.users[channel] = []

        # Remove leading ':' from first user.
        users[0] = users[0][1:]

        if channel not in self.users:
            self.users[channel] = users
        else:
            self.users[channel].extend(users)

        logger.info(" J | {}".format(self.users))

    def _handle_join(self, message):
        prefix, command, parameters = Irc.split_message(message)
        sender, user, ident = Irc.split_prefix(prefix)
        
        channel = parameters[1:]

        if sender == self.config['nick']:
            self.channels.append(channel)
            self.users[channel] = []
        else:
            self.users[channel].append(sender)

    def _handle_part(self, message):
        prefix, command, parameters = Irc.split_message(message)
        sender, user, ident = Irc.split_prefix(prefix)

        channel = parameters.split(" ")[0]

        if sender == self.config['nick']:
            self.users.pop(channel)
            for i, c in enumerate(self.channels):
                if c == channel:
                    self.channels.pop(i)
        else:
            for i, x in enumerate(self.users[channel]):
                if sender == x:
                    self.users[channel].pop(i)
 
    def _handle_mode(self, message):
        for channel in self.config['channels']:
            self.send(Irc.join(channel))

    def _handle_server_ping(self, message):
        prefix, command, parameters = Irc.split_message(message)

        # PONG any server PINGs with the same parameters.
        self.send(Irc.server_pong(parameters))

    def _handle_433(self, message):
        prefix, command, parameters = Irc.split_message(message)

        if re.search("Nickname is already in use", parameters):
            self.config['nick'] = "_{}".format(self.config['nick'])
            self.send(Irc.nick(self.config['nick']))
            self.send(Irc.user(self.config['user'], self.config['unused'],
                               self.config['owner']))
            self.send(Irc.mode(self.config['nick'], self.config['mode']))


class Irc:
    """
    This class provides IRC message format functions.
    These functions return a message ready to send.

    It also provides basic IRC utility functions.
    """

    msg_size = 475
    
    # Message Utility Functions
    @staticmethod
    def split_privmsg(message):
        channel, message = message.split(' ', 1)
        message = message[1:]

        return channel, message

    @staticmethod
    def split_message(message):
        prefix, command, parameters = None, None, None

        if message[0] == ':':
            prefix, msg = message.split(' ', 1)

            if ' ' in msg:
                command, parameters = msg.split(' ', 1)
            else:
                command = msg
        else:
            command, parameters = message.split(' ', 1)

        return prefix, command, parameters

    @staticmethod
    def split_prefix(prefix):
        nick, user, ident = None, None, None

        if prefix is not None:
            if '!' in prefix:
                nick = prefix.split('!')[0][1:]
                ident = prefix.split('!')[1]

                if '@' in ident:
                    user, ident = ident.split('@')
            else:
                nick = prefix
                ident = prefix

        return nick, user, ident

    @staticmethod
    def join_prefix(nick, user, ident):
        return "{}!{}@{}".format(nick, user, ident)

    @staticmethod
    def wrap_ctcp(message):
        return "\x01{}\x01".format(message)

    # Basic IRC Messages
    @staticmethod
    def notice(destination, message):
        return "NOTICE {} :{}".format(destination, message)

    @staticmethod
    def privmsg(destination, message):
        if len(message) == 0 or message is None:
            return None
        return "PRIVMSG {} :{}".format(destination, message)

    @staticmethod
    def nick(nick):
        return "NICK {}".format(nick)

    @staticmethod
    def user(user, unused, owner):
        return "USER {} {} {} {}".format(user, 0, unused, owner)

    @staticmethod
    def mode(nick, mode):
        return "MODE {} {}".format(nick, mode)

    @staticmethod
    def join(channel):
        return "JOIN {}".format(channel)

    @staticmethod
    def part(channel, message="Leaving"):
        return "PART {} {}".format(channel, message)

    @staticmethod
    def quit(quit_message="Quitting"):
        return "QUIT :{}".format(quit_message)

    @staticmethod
    def whois(nick):
        return "WHOIS {}".format(nick)
        
    # NICKSERV messages
    @staticmethod
    def register(owner_email, password):
        return Irc.privmsg("NICKSERV",
                           "REGISTER {} {}".format(owner_email, password))

    @staticmethod
    def identify(password):
        return Irc.privmsg("NICKSERV",
                           "IDENTIFY {}".format(password))

    # Special Messages
    @staticmethod
    def server_pong(message):
        """
        This should be used to respond to a server PING. The server PING
        comes with data that should be echoed in the PONG."""
        return "PONG {}".format(message)

    @staticmethod
    def ctcp_ping(destination, timestamp):
        """
        This is a CTCP ping sent to a destination and the expected response
        is a ctcp_pong with the same timestamp. The time delta from the
        ctcp_ping and the expected ctcp_pong gives an estimate travel time.
        """
        message = Irc.wrap_ctcp("PING {}".format(timestamp))
        return Irc.privmsg(destination, message)

    @staticmethod
    def ctcp_pong(destination, timestamp):
        """
        This is used to respond to ctcp_pings.
        """
        message = Irc.wrap_ctcp("PING {}".format(timestamp))
        return Irc.notice(destination, message)




