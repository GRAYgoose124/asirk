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
import importlib.util


logger = logging.getLogger(__name__)


class Plugin:
    def __init__(self, protocol):
        self.protocol = protocol

        self.admin_commands = {}
        self.commands = {}

    def msg_hook(self, prefix, command, parameters):
        raise NotImplemented


class PluginManager:
    def __init__(self, protocol, plugins_path):
        self.protocol = protocol

        self.plugins_path = plugins_path
        self.plugins = {}

        self.admin_commands = {}
        self.commands = {}

    def load_plugin(self, plugin_name):
        try:
            spec = importlib.util.spec_from_file_location(plugin_name,
                                                          os.path.join(self.plugins_path, "{}.py".format(plugin_name)))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            logger.warning(e)
            return

        try:
            plugin = getattr(module, plugin_name)(self.protocol)
        except AttributeError:
            logger.warning("Invalid Plugin: {}".format(plugin_name))
            return

        self.commands.update(plugin.commands)
        self.admin_commands.update(plugin.admin_commands)
        self.plugins[plugin_name] = plugin

    def unload_plugin(self, plugin_name):
        try:
            for key in self.plugins[plugin_name].commands:
                if key in self.commands:
                    self.commands.pop(key)

            for key in self.plugins[plugin_name].admin_commands:
                if key in self.admin_commands:
                    self.admin_commands.pop(key)

            self.plugins.pop(plugin_name)
        except KeyError:
            pass

    def load_plugins(self):
        for plugin_name in os.listdir(self.plugins_path):
            if plugin_name[-3:] == ".py" and plugin_name != "__init__.py":
                self.load_plugin(plugin_name[:-3])

    def unload_plugins(self):
        plugins_copy = self.plugins.copy()
        for plugin_name in plugins_copy:
            self.unload_plugin(plugin_name)

