
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
                self.protocol = protocol
                
                self.admin_commands = {}
                self.commands = {}
                
# Plugin command definition
self.commands = {'<command>': <command_function>}
def <command_function>(self, prefix, destination, message)

# Plugin hook definition
def privmsg_hook(self, prefix, command, parameters)
