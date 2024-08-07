# Bjornlang

Bjornlang is a custom DSL for writing scripts to interact with the display.

## Variable definitions

Variables can take numeric values. Variable names cannot start with an uppercase letter. They may contain lowercase and uppercase letters, numbers, and underscores.

```
apple = 10
some_variable = 23.15
_another_variable = 500
aLLGOOD = 15
```

## Strings and logging

Variables or strings can be logged to the console. Strings can be concatenated together via the `+` operator, and variables can be converted to strings with `str()`.

```
print("This is a log message!")

num_oranges = 5
print("I have " + str(num_oranges) + " oranges.")
```

The above code will output:
```
[LOG] This is a log message!
[LOG] I have 5 oranges.
```

Variables are **globally scoped**, meaning they can be accessed anywhere after definition.

## Mathematical operators

All standard `+`, `-`, `*`, and `/` operators are supported. Modulo is supported via the `%` operator, and bitwise shifting is supported via the `<<` and `>>` operators. Expressions can be used anywhere a numeric value is expected and can be assigned to variables.

## Mathematical functions

| Function     | Result                                              |
| :----------- | :-------------------------------------------------- |
| `round(x)`   | Returns `x` rounded based on Python rounding rules. |
| `ceil(x)`    | Returns the ceiling of `x`.                         |
| `floor(x)`   | Returns the floor of `x`.                           |
| `sqrt(x)`    | Returns the square root of `x`.                     |
| `pow(x, y)`  | Returns `x` raised to the power of `y`.             |
| `log(x, y)`  | Returns the base-`y` log of `x`.                    |
| `sin(x)`     | Returns sine of `x`.                                |
| `cos(x)`     | Returns cosine of `x`.                              |
| `int(x)`     | Returns `x` truncated.                              |
| `rand()`     | Returns a random float `y`, such that `0 <= y < 1`. |

## Built-in constants

| Constant     | Value                                         |
| :----------- | :-------------------------------------------- |
| `PI`         | Pi.                                           |
| `E`          | Euler's number.                               |
| `TIME`       | Time in seconds (fractional) since the epoch. |

## Code blocks

Code blocks contain instructions enclosed by braces (`{` and `}`).

```
{
    print("This is a code block.")
    print("It contains multiple instructions.")
}
```

## Macros

Macros can be defined with a code block. They can be called at any time after definition. Variables are globally scoped, so values must be defined inside the macro or before the macro is run.

```
num_apples = 1

print_something = {
    num_oranges = 2
    print("I have " + str(num_apples) + " apples and " + str(num_oranges) + " oranges.")
}

num_apples = 3
num_oranges = 4

print_something()
```

The above code will output:
```
[LOG] I have 3 apples and 2 oranges.
```

## If-else statements

If-else statements are supported for checking a single condition. Either a code block or an if-statement can be placed after an else-statement. If-statements do not have to be paired with an else statement. Supported conditional operators are `==`, `!=`, `<`, `>`, `<=` and `>=`.

```
x = 8

if x % 2 == 0 {
    print("x is even.")
} else {
    print("x is odd.")
}
```

The above will output:
```
[LOG] x is even.
```

Additionally, expressions can be used as conditions. If the expression evaluates to anything other than 0, then the condition will be true.

```
x = 0

if x {
    print("x is true.")
} else {
    print("x is false.")
}
```

The above will output:
```
[LOG] x is false.
```

## For-loops

For-loops are supported with ranges specified by starting and ending values. The loop variable will be incremented by one each loop if the ending value is greater than the starting value and decremented by one if the starting value is greater than the ending value. The start value is inclusive, while the end value is exclusive.

```
for x in (0, 3) {
    print("x is " + str(x) + ".")
}

for y in (10, 7) {
    print("y is " + str(y) + ".")
}
```

The above will output:
```
[LOG] x is 0.
[LOG] x is 1.
[LOG] x is 2.
[LOG] y is 10.
[LOG] y is 9.
[LOG] y is 8.
```

## Unicorn HAT functions

A few built-in functions are provided for interfacing with the Unicorn HAT display.

| Function                 | Result                                          |
| :----------------------- | :---------------------------------------------  |
| `display_clear()`        | Clears the display buffer.                      |
| `display_update()`       | Updates the display.                            |
| `set_pixel(x, y, color)` | Sets the pixel at position `(x, y)` to `color`. |

The following code demonstrates how to use these functions and randomly assigns a color to each pixel:
```
display_clear()

for x in (0, 16) {
    for y in (0, 16) {
        set_pixel(x, y, rgb(
            255 * rand(),
            255 * rand(),
            255 * rand()
        ))
    }
}

display_update()
```

### Color formats

Colors can be provided in two formats, hex and RGB.

| Color type               | Explanation                                                           |
| :----------------------- | :-------------------------------------------------------------------- |
| Hex: `$abcdef`           | Three two-digit hexadecimal values for red, green, and blue channels. |
| RGB: `rgb(r, g, b)`      | Three integers from 0 to 255 for red, green, and blue channels. Floats will be truncated. |

The following two `set_pixel` calls use equivalent colors:
```
set_pixel(x, y, $80ff40)
set_pixel(x, y, rgb(128, 255, 64))
```

## Comments

Comments are prefixed with a pound sign (`#`) and last for a single line.

```
# This is a comment
print("This is a statement.")
```