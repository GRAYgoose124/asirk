# Plugin format
Plugin.py:

        class <Plugin>:
            def __init__(self, protocol):
                super().__init__(protocol)
                
                self.admin_commands = {}
                self.commands = {}
    
                
## Plugin command definition
__init\__():

    self.commands = {'<command>': <command_function>}

self:

    def <command_function>(self, *event)
    *event = (prefix, destination, parameters)


## Plugin hook definition
    def msg_hook(self, *event)
    *event = (prefix, command, parameters)


## API Definitions
    self.protocol.users
    self.protocol.channels
    self.protocol.config 
    self.protocol.last_dest
    self.protocol.send_buffer


## API Function Definitions
Implemented in core.irc.IrcProtocol:

    self.protocol.send(message)
    self.protocol.send_response(destination, message)
