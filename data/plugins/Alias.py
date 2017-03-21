import logging

from lib.plugin import Plugin

logger = logging.getLogger(__name__)

class Alias(Plugin):
    def __init__(self, protocol):
        super().__init__(protocol)

        self.alias_list = {'dice': 'help'}
        
        self.commands = { 'newalias': self.newalias,
                          'oldalias': self.oldalias
                          }
        
    # TODO: Functionalize command usage in bot.py 
    def privmsg_hook(self, prefix, command, parameters):
        channel, message = parameters.split(' ', 1)
        message = message[1:]
                
        if message[0] == self.protocol.bot.command_symbol:
            cmd, params = message, ' '

            try:
                cmd, params = message.split(' ', 1)
                cmd = cmd[1:]
            except:
                pass
                
            if cmd in self.alias_list:
                alias_msg = (prefix, command, "{} :.{} {}".format(channel, self.alias_list[cmd], params))

                self.protocol.bot.process(*alias_msg)
                
                logger.info("ALS| Alias found: {} -> {}".format(cmd, self.alias_list[cmd]))
                
    
    def newalias(self, prefix, command, parameters):
        pass        
        
    def oldalias(self, prefix, command, parameters):
        pass
