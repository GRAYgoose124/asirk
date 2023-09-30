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
import json
import logging


logger = logging.getLogger(__name__)


def load_config(location):
    with open(location) as f:
        config = json.load(f)

    config["host"] = bytes(config["host"], "utf-8")
    config["port"] = bytes(config["port"], "utf-8")

    return config


def save_config(location, config):
    with open(location, "w") as f:
        json.dump(config, f)


def interactive_build_config(default_config, use_defaults=True):
    """
    Written with trust. Trust is evil, TODO: fix this.
    """
    config = default_config
    for key in default_config:
        t = type(default_config[key])
        if (
            (default_config[key] == "" or not use_defaults)
            or default_config[key] == []
            or default_config[key] == {}
            or default_config[key] is None
        ):
            if t is int:
                config[key] = int(input("{}: ".format(key)))
            if t is str:
                config[key] = str(input("{}: ".format(key)))
            if t is bool:
                config[key] = bool(input("{}: ".format(key)))
            if t is dict:
                config[key] = interactive_build_config(default_config[key])
            if t is list:
                print("Enter 'DONE' when finished.")
                inp = None
                config[key] = []
                while inp != "DONE":
                    if inp is not None:
                        config[key].append(inp)
                    inp = input("{}: ".format(key))

    return config
