Look at bot.py@106,123,127 for event* API 

# dedicated API file:
# API functions 
TODO: add irc_helpers
Addressed self.protocol.* in plugin.
    irc.IrcProtocol.send(message)
    irc.IrcProtocol.send_response(destination, message)

# Plugin format:
Plugin.py 
    
        class <Plugin>:
            def __init__(self, protocol):
                super().__init__(protocol)
                
                self.admin_commands = {}
                self.commands = {}
                
# Plugin command definition
self.commands = {'<command>': <command_function>}
# TODO eventdict*
def <command_function>(self, prefix, destination, message)

# Plugin hook definition
def privmsg_hook(self, prefix, command, parameters)


# Defs
self.protocol.users
self.protocol.channels
self.protocol.config <-> same config
self.protocol.last_dest
self.protocol.send_buffer
