import logging

from plugin import Plugin

logger = logging.getLogger(__name__)

class Calc(Plugin):
    def __init__(self, protocol):
        super().__init__(protocol)
        
        self.commands = { 'rpn': self.rpn,
                          }
    
    def rpn(self, prefix, destination, parameters):
        """<equation> -> RPN calculator"""
        try:
            equation = parameters.split(' ', 1)[1]
        except IndexError:
            return
                
        stack = []
                
        for op in equation.split(' '):
            try:
                v = float(op)
                stack.append(v)
            except ValueError:
                try:
                    if isinstance(op, str):
                        for c in op:
                            if c == '+':
                                a = stack.pop()
                                b = stack.pop()
                                stack.append(a + b)
                            elif c == '-':
                                a = stack.pop()
                                b = stack.pop()
                                stack.append(b - a)
                            elif c == '*':
                                a = stack.pop()
                                b = stack.pop()
                                stack.append(a * b)
                            elif c == '^':
                                a = stack.pop()
                                b = stack.pop()
                                if b < 10**10:
                                    stack.append(a ** b)
                            elif c == '|':
                                a = stack.pop()
                                b = stack.pop()
                                t = a ** b
                                c = a ** t
                                stack.append(c)
                            elif c == '/':
                                a = stack.pop()
                                b = stack.pop()
                                stack.append(b / a)
                except IndexError:
                    self.protocol.send_response(destination, "Invalid RPN: \"{}\", {}".format(equation, stack))
                    return 
                    
        self.protocol.send_response(destination, "Results: {}".format(stack))
