from sys import argv
from cmdline import parse_cmdline
from lang.interpret import BjornlangInterpreter

example_code = """
display_width = 16
display_height = 16

display_clear()
for x in (0, display_width) {
    for y in (0, display_height) {
        r = x / 16 * 255
        g = y / 16 * 255
        b = (x + y) / 32 * 255

        if int(get_time()) % 2 != 0 {
            set_pixel(x, y, rgb(r, g, b))
        } else {
            set_pixel(x, y, rgb(b, r, g))
        }
    }
}
display_update()
"""

unicorn = parse_cmdline(argv)
interpreter = BjornlangInterpreter(unicorn)
while True:
    interpreter.interpret(example_code)
