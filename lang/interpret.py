from os import path
import time
from lark import Lark, ParseTree, Token, Transformer, Tree, v_args
from operator import add, sub, mul, mod, truediv as div
from math import ceil, floor, sqrt, sin, cos, pow, log, pi, e
from random import random

from util import hex_to_rgb


class BjornlangInterpreter:

    _vars = {}
    _macros = {}
    _cache = {}

    def __init__(self, unicorn):
        self._unicorn = unicorn

        grammar_file = open(path.join(path.dirname(__file__), "grammar.txt"))
        self._parser = Lark(grammar_file.read())

    def interpret(self, code: str):
        # Check if the code is in the interpreter cache
        cache_key = hash(code)
        if cache_key in self._cache:
            self._run_instruction(self._cache[cache_key])
            return

        parse_tree = self._parser.parse(code)
        self._run_instruction(parse_tree)
        self._cache[cache_key] = parse_tree

    def repl(self):
        while True:
            s = input("> ")
            self.interpret(s)

    def reset(self):
        self._vars.clear()
        self._macros.clear()
        self._cache.clear()

    def _calc_expr(self, expr):
        if expr.data == "number":
            return float(expr.children[0].value)
        elif expr.data == "var":
            return self._vars[expr.children[0].value]
        elif expr.data == "neg":
            return -self._calc_expr(expr.children[0])
        elif expr.data == "add":
            return add(*map(self._calc_expr, expr.children))
        elif expr.data == "sub":
            return sub(*map(self._calc_expr, expr.children))
        elif expr.data == "mul":
            return mul(*map(self._calc_expr, expr.children))
        elif expr.data == "div":
            return div(*map(self._calc_expr, expr.children))
        elif expr.data == "mod":
            return mod(*map(self._calc_expr, expr.children))

        return self._calc_math_func_or_constant(expr)

    def _calc_math_func_or_constant(self, expr):
        # Math functions
        if expr.data == "to_int":
            return int(self._calc_expr(*expr.children))
        elif expr.data == "round":
            return round(self._calc_expr(*expr.children))
        elif expr.data == "ceil":
            return ceil(self._calc_expr(*expr.children))
        elif expr.data == "floor":
            return floor(self._calc_expr(*expr.children))
        elif expr.data == "sqrt":
            return sqrt(self._calc_expr(*expr.children))
        elif expr.data == "log2":
            return log(self._calc_expr(*expr.children), 2)
        elif expr.data == "sin":
            return sin(self._calc_expr(*expr.children))
        elif expr.data == "cos":
            return cos(self._calc_expr(*expr.children))
        elif expr.data == "pow":
            return pow(*map(self._calc_expr, expr.children))
        elif expr.data == "random":
            return random()

        # Constants
        if expr.data == "c_time":
            return time.time()
        elif expr.data == "c_pi":
            return pi
        elif expr.data == "c_e":
            return e

    def _format_string(self, value: Tree[Token]):
        if value.data == "string_literal":
            s = value.children[0]
            return s[1:-1]
        elif value.data == "to_string":
            val = self._calc_expr(*value.children)
            if val == int(val):
                return str(int(val))
            return str(val)
        elif value.data == "string":
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
        if condition.data == "var":
            return self._calc_expr(condition) != 0

        lh_side, rh_side = map(self._calc_expr, condition.children)

        if condition.data == "eq_check":
            return lh_side == rh_side
        elif condition.data == "neq_check":
            return lh_side != rh_side
        elif condition.data == "lt_check":
            return lh_side < rh_side
        elif condition.data == "gt_check":
            return lh_side > rh_side
        elif condition.data == "lteq_check":
            return lh_side <= rh_side
        elif condition.data == "gteq_check":
            return lh_side >= rh_side

        return False

    def _run_instruction(self, t: ParseTree):
        if t.data == "start" or t.data == "code_block":
            self._exec_code_block(t)
        elif t.data == "print":
            self._print_message(*t.children)
        elif t.data == "define_var":
            self._define_var(*t.children)
        elif t.data == "define_macro":
            self._define_macro(*t.children)
        elif t.data == "for_loop":
            self._for_loop(*t.children)
        elif t.data == "if_without_else":
            self._if_without_else(*t.children)
        elif t.data == "if_with_else":
            self._if_with_else(*t.children)
        elif t.data == "set_pixel":
            self._set_pixel(*t.children)
        elif t.data == "display_clear":
            self._display_clear()
        elif t.data == "display_update":
            self._display_update()
        elif t.data == "get_time":
            self._get_time()
        elif t.data == "use_macro":
            self._exec_macro(*t.children)

    def _parse_color(self, color: Tree[Token]):
        if color.data == "hex_color":
            return hex_to_rgb(color.children[0].value[1:])
        elif color.data == "rgb_color":
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
