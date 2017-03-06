import logging
import asyncio
import functools
import time

from irc import Irc, IrcProtocol


logger = logging.getLogger(__name__)


class IrcBot:
    def __init__(self, loop, config):
        self.client_completed = asyncio.Future()

        self.loop = loop
        self.config = config

        self.client = None
        self.transport, self.protocol = None, None

        self.commander = None

    def start(self):
        self.client = self.loop.create_connection(functools.partial(IrcProtocol,
                                                                    future=self.client_completed,
                                                                    config=self.config),
                                                  self.config['host'],
                                                  self.config['port'],
                                                  ssl=self.config['ssl'])

        self.transport, self.protocol = self.loop.run_until_complete(self.client)
        self.protocol.set_callback(self.process)

    def stop(self):
        self.protocol.send(Irc.quit("Stopping..."))
        self.transport.close()

        self.client = None
        self.transport, self.protocol = None, None

    # IrcProtocol message callback
    def process(self, prefix, command, parameters):
        raise NotImplementedError


class Irk(IrcBot):
    def __init__(self, loop, config):
        super().__init__(loop, config)

        self.admin_commands = {'quit': self._cmd_quit
                               }
        self.commands = {'ping': self._cmd_ping
                         }

        self.command_symbol = '.'
        self.commander = None

    def process(self, prefix, command, parameters):
        user, ident, host = prefix

        logger.debug("   |  {},{},{}".format(prefix, command, parameters))

        if command == 'PRIVMSG':
            self.commander = user
            destination, message = Irc.split_privmsg(parameters)

            bot_cmd = message.split(' ')[0]
            if self.command_symbol == bot_cmd[0]:
                bot_cmd = bot_cmd[1:]

                if self.commander == self.config['owner']:
                    for k, v in self.admin_commands.items():
                        if bot_cmd == k:
                            v(prefix, destination, message)

                for k, v in self.commands.items():
                    if bot_cmd == k:
                        v(prefix, destination, message)

        elif command == 'NOTICE':
            pass

        elif command == '401':
            self.protocol.send_response(self.protocol.last_dest, "That nick is invalid.")

    # Bot commands
    def _cmd_ping(self, prefix, channel, parameters):
        user = parameters.split(' ')[1]

        unix_timestamp = str(time.time()).replace(".", " ")
        self.protocol.send(Irc.ctcp_ping(user, unix_timestamp))
        logger.info("PNG| {}".format(user))


    def _cmd_quit(self, prefix, channel, parameters):
        self.stop()