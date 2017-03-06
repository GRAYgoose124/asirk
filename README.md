# API functions
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