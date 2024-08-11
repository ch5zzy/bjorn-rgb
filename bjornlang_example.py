import argparse
from sys import argv
from cmdline import parse_cmdline
from lang.interpret import BjornlangInterpreter
from util import import_unicorn

args = parse_cmdline(
    argv,
    repl={"action": "store_true", "default": False},
    file={"action": "store", "default": None},
)

if args.repl:

    class FakeUnicorn:

        def __init__(self):
            self.log("initialized!")

        def log(self, message):
            print(f"[FAKE_UNICORN] {message}")

        def set_pixel(self, x, y, r, g, b):
            self.log(f"set_pixel({x}, {y}, {r}, {g}, {b})")

        def show(self):
            self.log("show()")

        def clear(self):
            self.log("clear()")

        def off(self):
            self.log("off()")
            pass

    interpreter = BjornlangInterpreter(FakeUnicorn())
    interpreter.repl()


if args.file != None:
    file = open(args.file)
else:
    file = open("lang/example.bjl")

code = file.read()
file.close()

unicorn = import_unicorn(args.sim)
interpreter = BjornlangInterpreter(unicorn)
while True:
    interpreter.interpret(code)
