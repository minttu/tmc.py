from functools import partial
from sys import stdout, stderr
from os import getenv

# User might want to disable all coloring
no_coloring = getenv("TMCPY_NOCOLORING", False)


class AnsiColorCodes(object):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    RESET = 39


# Creates an escaped ANSI color/style character
to_escaped = lambda x: "\033[{0}m".format(x)


class Escaped(object):
    """ Helper class for translating AnsiColorCodes (or similar) to escaped"""
    def __init__(self, codes):
        for item in dir(codes):
            if item.startswith("_"):
                continue
            val = "" if no_coloring else to_escaped(getattr(codes, item))
            setattr(self, item, val)


# Use this to refer to escaped color characters
# Example: print(Colors.RED + "Hello" + Colors.RESET)
Colors = Escaped(AnsiColorCodes)


def formatter(color, s):
    """ Formats a string with color """
    return "{begin}{s}{reset}".format(begin=color, s=s, reset=Colors.RESET)


class Printer(object):
    """
    Context manager for printing in specific color
    Uses terminal character codes defined in colorama-module.

    Example:
        with Printer(Colors.RED, sys.stdout.writer) as wr:
            wr("This will be in red")
            wr("So will this")

    """
    def __init__(self, color, output):
        """
        Args:
            color: One of the character codes from colorama-module.
            output: An object that has .write method (e.g sys.stdout)
        """
        self.color = color
        self.output = output.write

    def __enter__(self):
        self.output(self.color)
        return self.output

    def __exit__(self, exc_ty, exc_val, tb):
        self.output(Colors.RESET)
        self.output = None


# Use one of these to print multiple lines in a specific
# color context.
ErrorPrinter = partial(Printer, Colors.RED, stderr)
WarningPrinter = partial(Printer, Colors.YELLOW, stderr)
SuccessPrinter = partial(Printer, Colors.GREEN, stdout)
InfoPrinter = partial(Printer, Colors.CYAN, stdout)

# These are useful is you have only a few lines you want
# to print with specific color context
as_error = partial(formatter, Colors.RED)
as_warning = partial(formatter, Colors.YELLOW)
as_success = partial(formatter, Colors.GREEN)
as_info = partial(formatter, Colors.CYAN)


# Directly print out with coloring
def errormsg(s):
    print(as_error(s), file=stderr)


def warningmsg(s):
    print(as_warning(s), file=stderr)


def successmsg(s):
    print(as_success(s), file=stdout)


def infomsg(s):
    print(as_info(s), file=stdout)
