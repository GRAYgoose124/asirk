#   asIrk: asyncio irc bot
#   Copyright (C) 2017  Grayson Miller
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
import time
import os
import atexit
import sys

from asirk.core.plugin import Plugin


logger = logging.getLogger(__name__)


GIT_SOURCE = "https://github.com/GRAYgoose124/asirk"


class BotUtils(Plugin):
    def __init__(self, protocol):
        super().__init__(protocol)

        self.commands = {
            "echo": self.echo,
            "uptime": self.uptime,
            "help": self.help,
            "docs": self.mysource,
        }

        self.admin_commands = {
            "bound": self.bound,
            "conf": self.config,
            "restart": self.restart,
            "quit": self.quit,
        }

    def msg_hook(self, event):
        pass

    def echo(self, event):
        """<message> -> bot: <message>"""
        if event.dest == self.protocol.config["nick"]:
            dest = event.user
        else:
            dest = event.dest

        self.protocol.respond(dest, " ".join(event.msg.split(" ")[1:]))

    def mysource(self, event):
        """-> returns git url."""
        msg = "My most recently published source can be found here: {}"
        self.protocol.respond(event.dest, msg.format(GIT_SOURCE))

    def uptime(self, event):
        """-> returns the average process time and uptime of the bot."""
        up = (time.time() - self.protocol.starttime) / 60
        self.protocol.respond(event.dest, "Uptime: {:.2f} minutes.".format(up))

    def config(self, event):
        """-> returns the bot's current configuration."""
        self.protocol.send_notice(event.user, "config: {}".format(self.protocol.config))

    def quit(self, event):
        """-> stops the bot and shuts it down."""
        self.protocol.bot.stop()

    def restart(self, event):
        """-> stops the bot and restarts it."""

        def __restart():
            # TODO: Does not work on windows with spaces in exe path.
            python = sys.executable
            os.execl(python, python, *sys.argv)

        atexit.register(__restart)
        self.protocol.bot.stop()

    def bound(self, event):
        """<command> -> What plugin that command comes from"""
        _, bound_cmd, *_ = event.msg.split(" ", 2)

        acl = self.protocol.bot.admin_commands.copy()
        command_list = dict(self.protocol.bot.commands, **acl)

        if bound_cmd == "all":
            d = {}
            for n, c in command_list.items():
                cn = str(c.__self__.__class__).split("'")[1]
                cn = cn.split(".")[1]

                if cn not in d:
                    d[cn] = [n]
                else:
                    d[cn].append(n)

            msg = str(d).translate(
                {
                    ord(k): v
                    for k, v in {
                        ",": None,
                        "{": None,
                        "}": None,
                        "[": None,
                        "]": "\r\n",
                        "'": None,
                    }.items()
                }
            )
            messages = msg.split("\r\n")

            try:
                for m in messages:
                    if m[0] == " ":
                        m = m[1:]
                    self.protocol.respond(event.dest, m)
            except IndexError:
                pass
        else:
            try:
                msg = command_list[bound_cmd].__self__.__class__
            except KeyError:
                return

            s = str(msg).split("'")[1].split(".")[1]
            msg = "Command '{}' from '{}'".format(bound_cmd, s)

            self.protocol.respond(event.dest, msg)

    def help(self, event):
        """<command> -> extra information on using <command>."""
        cmds = []

        try:
            help_cmd = event.msg.split(" ")[1]

            if help_cmd == "all":
                for cmd in self.protocol.bot.admin_commands:
                    self._single_help(cmd, event.dest)
                for cmd in self.protocol.bot.commands:
                    self._single_help(cmd, event.dest)
            else:
                self._single_help(help_cmd, event.dest)
        except IndexError:
            cmds += ["{}*".format(cmd) for cmd in self.protocol.bot.admin_commands]
            cmds += [cmd for cmd in self.protocol.bot.commands]

            self.protocol.respond(event.dest, ", ".join(cmds))

    def _single_help(self, help_cmd, destination):
        try:
            for line in self.protocol.bot.commands[help_cmd].__doc__.split("\n"):
                self.protocol.respond(destination, "{} {}".format(help_cmd, line))
                return
        except (ValueError, IndexError):
            pass
        try:
            for line in self.protocol.bot.admin_commands[help_cmd].__doc__.split("\n"):
                self.protocol.respond(destination, "{} {}".format(help_cmd, line))
            return
        except (ValueError, IndexError):
            pass
