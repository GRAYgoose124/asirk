import logging
import os.path
import traceback

from asirk.core.plugin import Plugin


logger = logging.getLogger(__name__)


class Log(Plugin):
    def __init__(self, protocol):
        super().__init__(protocol)

        self.send_buffer_index = 0

        self.log_file = os.path.join(
            self.protocol.config["plugin_data_path"], "log.txt"
        )
        # create file if it doesn't exist
        if not os.path.isfile(self.log_file):
            # ensure directory with mkdirs
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

            # touch file
            with open(self.log_file, "w") as f:
                pass

    def msg_hook(self, event):
        # TODO API file hook
        with open(self.log_file, "a+") as f:
            try:
                f.write(
                    "{1}/{0}: {2}".format(event.prefix[0], *event.params.split(" ", 1))
                )
                f.write(self.protocol.send_buffer[self.send_buffer_index :])
            except (IndexError, ValueError) as e:
                pass
                # logger.debug(" X | Uh-oh! Somethin's dun fucked!")
                # traceback.print_exc(e)

        self.send_buffer_index = len(self.protocol.send_buffer) - 1
