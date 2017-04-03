import logging
import os.path 

from core.plugin import Plugin


logger = logging.getLogger(__name__)


class Log(Plugin):
    def __init__(self, protocol):
        super().__init__(protocol)

        self.send_buffer_index = 0

    def msg_hook(self, event):
        # TODO API file hook
        with open(os.path.join(self.protocol.config['plugin_data_path'],
                               'log.txt'), 'a+') as f:
            try:
                f.write("{1}/{0}: {2}".format(event.prefix[0],
                                              *event.params.split(' ', 1)))
                f.write(self.protocol.send_buffer[self.send_buffer_index:])
            except (IndexError, ValueError) as e:
                logger.debug(" X | Uh-oh! Somethin's dun fucked!")

        self.send_buffer_index = len(self.protocol.send_buffer) - 1
