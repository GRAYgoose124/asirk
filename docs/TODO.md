## Warning: The following is essentially just a scratch pad at the moment.

Plugin.protocol -> Plugin.bot? 
Then have plugins provide helper functions for sending messages etc...
move helpers into bot? 
ie self.bot.protocol.send_response -> self.bot.send_response
Then remove IrcProtocol.set_bot and related

cull protocol.users in favor of protocol.channel

group structure commands
make commands like callable dicts with subdicts?
TODO: (w/ new structure)
join
joined
part
to
irc join
irc list
irc part

authentication structure (login cmd)
Plugin 'uniforms'
Plugin GC when unloaded
Full checking for plugin functions.
.restart enable/disable debug params

config (then you can remove your custom config.json from the repo)
arguments   
argparsing and file loading for config
argparsing: debug, datapath, verbosity
generate config
Generate homes (plugins+config dir scripts)
permanent default config/plugin folder

Plugins:
-markov chain inspired factoids? GA? ANN?
macros
link-get
default enabled plugins list
prolog like engine

Standardize how commands split parameters, etc.