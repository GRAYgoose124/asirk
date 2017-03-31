import logging
import os

from core.plugin import Plugin

logger = logging.getLogger(__name__)

class Todo(Plugin):
    def __init__(self, protocol):
        super().__init__(protocol)
        
        # TODO: Structured command API
        self.commands = {'todo': self.todo,
                         'todolist': self.list
                        }
        self.admin_commands = {'todorm': self.delete
                              }
                              
    def todo(self, prefix, destination, parameters):
        """<message> -> creates a single line message and saves it."""
        with open(os.path.join(self.protocol.config['plugin_data_path'], 'todo.txt'), 'a+') as f:
            f.write("{}\n".format(parameters.split(' ', 1)[1]))        
        
        self.protocol.send_response(destination, "Note recorded.")
        
    def list(self, prefix, destination, parameters):
        # TODO plugin API helpers
        try:
            index = int(parameters.split(' ')[1])
        except (IndexError, ValueError):
            index = None
                        
        self.protocol.send_response(destination, "Task List:")
        
        with open(os.path.join(self.protocol.config['plugin_data_path'], 'todo.txt'), 'r') as f:
            for i, line in enumerate(f.readlines()):
                if index is None or index == i:
                    self.protocol.send_response(destination, "  {}: {}".format(i, line).strip('\n'))

        self.protocol.send_response(destination, "---------")

    def delete(self, prefix, destination, parameters):
        index = parameters.split(' ')[1]
        note = ""

        if index == 'all':
            open(os.path.join(self.protocol.config['plugin_data_path'], 'todo.txt'), 'w')
            self.protocol.send_response(destination, "All notes removed.")
            return
        
        index = int(index)
        with open(os.path.join(self.protocol.config['plugin_data_path'], 'todo.txt'), 'r+') as f:
            lines = []
            for num, line in enumerate(f.readlines()):
                if index != num:
                    lines.append(line)
                else:
                    note = line
            f.seek(0)
            f.truncate()
            f.writelines(lines)                
                            
        self.protocol.send_response(destination, "{} removed.".format(note))
