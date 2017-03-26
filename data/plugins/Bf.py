#   Irk: irc bot
#   Copyright (C) 2016  Grayson Miller
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
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>
import logging

from lib.plugin import Plugin


logger = logging.getLogger(__name__)


class Bf(Plugin):
    def __init__(self, protocol):
        super().__init__(protocol)
        self.commands = {
            'bf': self.bf
        }

    def bf(self, prefix, destination, parameters):
        """<code> -> Brainfuck interpreter results."""
        # TODO: API split parameter function
        try:
            code_string = None
            _, code_string, *input_string = parameters.split(" ", 2)
            input_string = input_string[0]
            code_string = code_string.strip(' ')
        except (IndexError, ValueError):
            pass

        if code_string is None or code_string == '':
            self.protocol.send_response(destination, "Invalid BF command.")
            return
                
        max_loops = 1024
        tape_size = 24
        tape = [0]*tape_size
        tape_pos = int(tape_size / 2)
        i_saved = []

        output_string = ""

        loop_n = 0
        i = 0
        # TODO: Look at BID, fix bf code
        while i < len(code_string):
            if code_string[i] == '+':
                tape[tape_pos] += 1
            elif code_string[i] == '-':
                tape[tape_pos] -= 1
            elif code_string[i] == '>':
                if tape_pos >= tape_size-1:
                    tape_pos = 0
                else:
                    tape_pos += 1
            elif code_string[i] == '<':
                if tape_pos == 0:
                    tape_pos = tape_size-1
                else:
                    tape_pos -= 1
            elif code_string[i] == ']':
                if tape[tape_pos] != 0 and loop_n < max_loops:
                    i = i_saved.pop()
                    loop_n += 1
                elif loop_n > max_loops:
                    loop_n = 0
            elif code_string[i] == '[':
                i_saved.append(i-1)
            elif code_string[i] == ',':
                if input_string != "":
                    tape[tape_pos] = ord(input_string[0])
                    input_string = input_string[1:]
                else:
                    break
            elif code_string[i] == '.':
                output_string += chr(tape[tape_pos])
            i += 1

        # TODO: Filter output string
        if output_string != "":
            message = "BF Output: " + output_string
        else:
            message = repr(tape)

        self.protocol.send_response(destination, message)
