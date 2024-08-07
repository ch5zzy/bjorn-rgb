from os import path
import time
from lark import Lark, ParseTree, Token, Transformer, Tree, v_args

from util import hex_to_rgb


class BjornlangInterpreter:

    _vars = {}
    _macros = {}

    @v_args(inline=True)
    class MathTransformer(Transformer):
        from operator import add, sub, mul, mod, truediv as div, neg
        from math import ceil, floor, sqrt, sin, cos, pow, log, pi, e

        number = float

        def var(self, name: str):
            return BjornlangInterpreter._vars[name]

        def lshift(self, value, shift):
            return int(value) << int(shift)

        def rshift(self, value, shift):
            return int(value) >> int(shift)

        def round(self, value):
            return round(value)

        def to_int(self, value):
            return int(value)

        def c_pi(self):
            return self.pi

        def c_e(self):
            return self.e

        def c_time(self):
            return time.time()

    def __init__(self, unicorn):
        self._unicorn = unicorn

        grammar_file = open(path.join(path.dirname(__file__), "grammar.txt"))
        self._parser = Lark(grammar_file.read())
        self._math_transformer = self.MathTransformer()

    def interpret(self, code: str):
        self._run_instruction(self._parser.parse(code))

    def repl(self):
        while True:
            s = input("> ")
            self.interpret(s)

    def _calc_expr(self, expr: Token | Tree[Token]):
        return self._math_transformer.transform(expr)

    def _format_string(self, value: Tree[Token]):
        match value.data:
            case "string_literal":
                s = value.children[0]
                return s[1:-1]
            case "to_string":
                val = self._calc_expr(*value.children)
                if val == int(val):
                    return str(int(val))
                return str(val)
            case "string":
                s = ""
                for substr in value.children:
                    s += self._format_string(substr)
                return s

    def _print_message(self, value: Tree[Token]):
        print("[LOG]", self._format_string(value))

    def _define_var(self, name: Token, value: Tree[Token]):
        self._vars[name.value] = self._calc_expr(value)

    def _define_macro(self, name: Token, code_block: Tree[Token]):
        self._macros[name.value] = code_block

    def _exec_macro(self, name: Token):
        self._exec_code_block(self._macros[name.value])

    def _for_loop(
        self, name: Tree[Token], var_range: Tree[Token], code_block: Tree[Token]
    ):
        start, stop = map(self._calc_expr, var_range.children)

        for i in range(int(start), int(stop), -1 if stop < start else 1):
            self._vars[name.value] = i
            self._exec_code_block(code_block)

    def _if_without_else(self, condition: Tree[Token], code_block: Tree[Token]):
        should_exec = self._eval_condition(*condition.children)

        if should_exec:
            self._exec_code_block(code_block)

        return should_exec

    def _if_with_else(self, if_statement, else_statement):
        if not self._if_without_else(*if_statement.children):
            self._run_instruction(else_statement)

    def _exec_code_block(self, code_block: Tree[Token]):
        for inst in code_block.children:
            self._run_instruction(inst)

    def _eval_condition(self, condition: Tree[Token]):
        print(condition)
        if condition.data == "var":
            return self._calc_expr(condition) != 0

        lh_side, rh_side = map(self._calc_expr, condition.children)

        match condition.data:
            case "eq_check":
                return lh_side == rh_side
            case "neq_check":
                return lh_side != rh_side
            case "lt_check":
                return lh_side < rh_side
            case "gt_check":
                return lh_side > rh_side
            case "lteq_check":
                return lh_side <= rh_side
            case "gteq_check":
                return lh_side >= rh_side

        return False

    def _run_instruction(self, t: ParseTree):
        match t.data:
            case "code_block" | "start":
                self._exec_code_block(t)
            case "print":
                self._print_message(*t.children)
            case "define_var":
                self._define_var(*t.children)
            case "define_macro":
                self._define_macro(*t.children)
            case "for_loop":
                self._for_loop(*t.children)
            case "if_without_else":
                self._if_without_else(*t.children)
            case "if_with_else":
                self._if_with_else(*t.children)
            case "set_pixel":
                self._set_pixel(*t.children)
            case "display_clear":
                self._display_clear()
            case "display_update":
                self._display_update()
            case "get_time":
                self._get_time()
            case "use_macro":
                self._exec_macro(*t.children)

    def _parse_color(self, color: Tree[Token]):
        match color.data:
            case "hex_color":
                return hex_to_rgb(color.children[0].value[1:])
            case "rgb_color":
                rgb = map(int, map(self._calc_expr, color.children))
                return tuple(rgb)

    def _set_pixel(self, x: Tree[Token], y: Tree[Token], color: Tree[Token]):
        self._unicorn.set_pixel(
            int(self._calc_expr(x)),
            int(self._calc_expr(y)),
            *self._parse_color(*color.children),
        )

    def _display_clear(self):
        self._unicorn.clear()

    def _display_update(self):
        self._unicorn.show()
