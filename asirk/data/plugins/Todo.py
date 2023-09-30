import logging
import os

from asirk.core.plugin import Plugin


logger = logging.getLogger(__name__)


class Todo(Plugin):
    def __init__(self, protocol):
        super().__init__(protocol)

        # TODO: Structured command API
        self.commands = {"todo": self.todo, "todolist": self.list}
        self.admin_commands = {"todorm": self.delete}

    def msg_hook(self, event):
        pass

    def todo(self, event):
        """<message> -> creates a single line message and saves it."""
        with open(
            os.path.join(self.protocol.config["plugin_data_path"], "todo.txt"), "a+"
        ) as f:
            f.write("{}\n".format(event.msg.split(" ", 1)[1]))

        self.protocol.respond(event.dest, "Note recorded.")

    def list(self, event):
        # TODO plugin API helpers
        try:
            index = int(event.msg.split(" ")[1])
        except (IndexError, ValueError):
            index = None

        self.protocol.respond(event.dest, "Task List:")

        with open(
            os.path.join(self.protocol.config["plugin_data_path"], "todo.txt"), "r"
        ) as f:
            for i, line in enumerate(f.readlines()):
                if index is None or index == i:
                    self.protocol.respond(
                        event.dest, "  {}: {}".format(i, line).strip("\n")
                    )

        self.protocol.respond(event.dest, "---------")

    def delete(self, event):
        index = event.msg.split(" ")[1]
        note = ""

        if index == "all":
            open(
                os.path.join(self.protocol.config["plugin_data_path"], "todo.txt"), "w"
            )
            self.protocol.respond(event.dest, "All notes removed.")
            return

        index = int(index)
        with open(
            os.path.join(self.protocol.config["plugin_data_path"], "todo.txt"), "r+"
        ) as f:
            lines = []
            for num, line in enumerate(f.readlines()):
                if index != num:
                    lines.append(line)
                else:
                    note = line
            f.seek(0)
            f.truncate()
            f.writelines(lines)

        self.protocol.respond(event.dest, "{} removed.".format(note))
