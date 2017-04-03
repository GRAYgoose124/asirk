#   asIrk: asyncio irc bot
#   Copyright (C) 2017 Grayson Miller
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>
import logging
import os
import traceback

from importlib.util import spec_from_file_location, module_from_spec


logger = logging.getLogger(__name__)


class Plugin:
    def __init__(self, protocol):
        self.protocol = protocol

        self.admin_commands = {}
        self.commands = {}

    def msg_hook(self, event):
        raise NotImplementedError


class PluginManager:
    def __init__(self, protocol, plugins_path):
        self.protocol = protocol

        self.plugins_path = plugins_path
        self.plugins = {}

        self.admin_commands = {}
        self.commands = {}

    def list_plugins(self):
        for name in os.listdir(self.plugins_path):
            if name[-3:] == ".py" and \
               name != "__init__.py" and \
               name[:2] != ".#":
                yield name

    def load_plugin(self, name):
        if name in self.plugins:
            self.unload_plugin(name)

        try:
            script = os.path.join(self.plugins_path,
                                  "{}.py".format(name))
            spec = spec_from_file_location(name, script)
            module = module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            logger.warning(" ~ | {}".format(e))
            traceback.print_tb(e.__traceback__)
            return

        try:
            # TODO: !!! self.protocol -> self (bot) then bot plugin helpers.
            # Put other bot helpers in IrcProtocol in Irk.
            plugin = getattr(module, name)(self.protocol)
        except AttributeError as e:
            logger.warning(" ~ | Invalid Plugin: {}".format(name))
            traceback.print_tb(e.__traceback__)
            return

        logger.debug(" + | {}: {}".format(name,
                                          plugin.commands))

        try:
            self.commands.update(plugin.commands)
            self.admin_commands.update(plugin.admin_commands)
            self.plugins[name] = plugin
            
            return True
        except (ValueError, TypeError) as e:
            logger.warning("PGN| ERROR")
            traceback.print_tb(e.__traceback__) 

    def unload_plugin(self, name):
        try:
            for key in self.plugins[name].commands:
                if key in self.commands:
                    self.commands.pop(key)

            for key in self.plugins[name].admin_commands:
                if key in self.admin_commands:
                    self.admin_commands.pop(key)

            self.plugins.pop(name)
            logger.debug(" - | {} unloaded.".format(name))

        except KeyError:
            pass

    def load_plugins(self):
        for plugin_name in os.listdir(self.plugins_path):
            if plugin_name[-3:] == ".py" and \
               plugin_name != "__init__.py" and \
               plugin_name[:2] != ".#":
                self.load_plugin(plugin_name[:-3])

    def unload_plugins(self):
        plugins_copy = self.plugins.copy()
        for plugin_name in plugins_copy:
            self.unload_plugin(plugin_name)

