import logging

from asirk.core.plugin import Plugin


logger = logging.getLogger(__name__)


class Calc(Plugin):
    def __init__(self, protocol):
        super().__init__(protocol)

        self.commands = {"rpn": self.rpn}

    def msg_hook(self, event):
        pass

    def rpn(self, event):
        """<equation> -> RPN calculator"""
        try:
            equation = event.msg.split(" ", 1)[1]
        except IndexError:
            return

        stack = []

        msg = None
        for op in equation.split(" "):
            try:
                v = float(op)
                stack.append(v)
            except ValueError:
                try:
                    if isinstance(op, str):
                        for c in op:
                            if c == "+":
                                a = stack.pop()
                                b = stack.pop()
                                stack.append(a + b)
                            elif c == "-":
                                a = stack.pop()
                                b = stack.pop()
                                stack.append(b - a)
                            elif c == "*":
                                a = stack.pop()
                                b = stack.pop()
                                stack.append(a * b)
                            elif c == "^":
                                a = stack.pop()
                                b = stack.pop()
                                if b < 10**10:
                                    stack.append(a**b)
                            elif c == "|":
                                a = stack.pop()
                                b = stack.pop()
                                t = a**b
                                c = a**t
                                stack.append(c)
                            elif c == "/":
                                a = stack.pop()
                                b = stack.pop()
                                stack.append(b / a)
                    msg = "Results: {}".format(stack)
                except IndexError:
                    msg = 'Invalid RPN: "{}", {}'.format(equation, stack)

        self.protocol.respond(event.dest, msg)
