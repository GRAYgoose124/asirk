import logging

from plugin import Plugin

logger = logging.getLogger(__name__)

class Log(Plugin):
      def __init__(self, protocol):
          super().__init__(protocol)

      def privmsg_hook(self, prefix, command, parameters):
            with open('/home/goose/log.txt', 'a+') as f:
                  f.write("{1}/{0}: {2}\n".format(prefix[0], *parameters.split(' ', 1)))
