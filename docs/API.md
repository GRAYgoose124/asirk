# Plugin format
Plugin.py:

        class <Plugin>:
            def __init__(self, protocol):
                super().__init__(protocol)
                
                self.admin_commands = {}
                self.commands = {}
    
                
## Plugin command definition
self.__init\__():

    self.commands = {'<command>': <command_function>}

self:

    def <command_function>(self, event)
    event = (user, destination, message)
        BotEvent = namedtuple('BotEvent', 'user dest msg')

## Plugin hook definition
    def msg_hook(self, event)
    event = (prefix, command, parameters)
        IrcEvent = namedtuple('IrcEvent', 'prefix cmd params')

## API Definitions (Plugin perspective)
    # To be changed to self.bot.*
    self.protocol.users # To be removed in favor of channels.
    self.protocol.channels
    self.protocol.config 
    self.protocol.last_dest # Use this in msg_hooks to respond to queries.
    self.protocol.send_buffer

## API Function Definitions
Implemented in core.irc.IrcProtocol:

    self.protocol.send(message)
    self.protocol.respond(destination, message)


    
