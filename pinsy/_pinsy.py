# Copyright 2024 Anas Shakeel
# from __future__ import annotations

import sys
import json
import platform
import ipaddress
import re
from re import Pattern
from math import floor, ceil
from textwrap import fill
from getpass import getpass
from pathlib import Path
from datetime import datetime
from time import sleep
from calendar import month as calendar_month
from itertools import batched
from os.path import isfile, isdir, splitext, join as path_join, sep as path_sep, normpath
from ansy import (colored, colored_ansy, make_ansi, de_ansi,
                  create_style, is_valid_color, ANSI_REGEX,
                  ANSI_CODES, ATTRIBUTES, Attribute, Color, ColorMode)
from ansy.exceptions import InvalidColorError
from .cursor import HiddenCursor
from . import utils
from .utils import get_terminal_size, typecheck
from ._others import (PromptChar, FillChar, Charset, YAlign, XAlign, Bullet,
                      StrConstraint, Callback, ErrorHandling,
                      ERROR_HANDLING, CONSTRAINTS, CHARSETS, REGEX_PATTERNS)
from typing import List, Tuple, Dict, Iterable, Callable, Literal, Optional, Union, Any


class Pins:
    """ 
    ### Pins
    This is the `1st` and main class of the `pinsy` package.

    #### ARGS:
    - `use_colors`: as name implies, Use colors (default `True`)
    - `handle_errors`: how should Pins handle errors (`raise`, `quit`, `callback`)
    - `error_callback`: function to call on errors, when handle_errors is set to `callback`
    - `charset`: the character set to use (`ascii`, `blocks`, `box`, `box_double`, `box_heavy`, `box_round`)
    - `prompt_char`: prompt character(s) to use in input functions.
    - `color_mode`: color mode to use (`4`, `8`, `24`)

    #### Example Usage:
    ```
    >> from pinsy import Pins
    >>
    >> pins = Pins()
    >> pins.colorize('Color this text red.', fgcolor='red')
    'Color this text red.'
    ```
    """

    def __init__(self, use_colors: bool = True,
                 handle_errors: ErrorHandling = 'quit',
                 error_callback: Callback | None = None,
                 charset: Charset = 'ascii',
                 prompt_char: PromptChar = '>>',
                 color_mode: int = 4) -> None:

        self.OS: str = platform.system()  # Windows | Linux | Darwin
        if self.OS == "Windows":
            Pins.fix_windows_console()

        # Erros and Callbacks
        assert isinstance(handle_errors, str), \
            "handle_errors must be a string."

        if handle_errors not in ERROR_HANDLING:
            raise ValueError(f"Invalid handle_errors: '{handle_errors}'")

        if handle_errors == "callback":
            if not error_callback:
                raise NameError(
                    "cannot set handle_errors to 'callback' without providing a callback.")
            elif not callable(error_callback):
                raise TypeError(f"'error_callback' expects a function not {
                                type(error_callback)}")

        self.ARGS: dict = {}
        self.error_callback = error_callback
        self.handle_errors = handle_errors
        self.USE_COLORS: bool = use_colors

        # Set self.COLORMODE & self.DEFAULT_COLORS
        self.set_colormode(color_mode)

        # Set self.CHARSET & self.charset_name
        self.set_charset(charset)

        # Char used in make_status
        self.STATUS_CHAR = "█"
        self.PROMPT_CHAR = prompt_char if prompt_char else ">>"

    @classmethod
    def fix_windows_console(cls):
        """ Fix windows terminal (ancient ones like powershell, cmd etc.) """
        try:
            from colorama import just_fix_windows_console
            just_fix_windows_console()
        except ModuleNotFoundError:
            print(f"colorama is not installed")
            exit(1)

    def enable_colors(self):
        """ Enable Terminal Colors. Just a convenience function to enable colors. """
        self.USE_COLORS = True

    def disable_colors(self):
        """ Disable Terminal Colors. Just a convenience function to disable colors. """
        self.USE_COLORS = False

    def set_colormode(self, mode: int):
        """
        ### Set Colormode
        Change/override the pins.COLORMODE. 
        
        Raises `AssertionError` if:
        - `mode` is not `4`, `8` or `24`.
        """
        assert mode in (4, 8, 24), f"Invalid mode: {mode}"
        self.COLORMODE = mode
        self.DEFAULT_COLORS = self._assign_colors()

    def set_default_colors(self, error: Color = None,
                           info: Color = None,
                           success: Color = None,
                           warn: Color = None):
        """ 
        ### Set Default Colors
        Change the default colors of certain things like errors & info messages etc.
        """
        self._validate_colors([("error", error), ("info", info),
                               ("success", success), ("warn", warn)])

        self.DEFAULT_COLORS['error'] = error if error else self.DEFAULT_COLORS['error']
        self.DEFAULT_COLORS['info'] = info if info else self.DEFAULT_COLORS['info']
        self.DEFAULT_COLORS['success'] = success if success else self.DEFAULT_COLORS['success']
        self.DEFAULT_COLORS['warn'] = warn if warn else self.DEFAULT_COLORS['warn']

    def set_charset(self, charset:Charset):
        """  
        ### Set Charset
        Change/override the pins.CHARSET.
        
        Raises `AssertionError` if:
        - `charset` is invalid
        """
        assert charset in CHARSETS, f"Invalid charset: '{charset}'"
        self.CHARSET: dict = CHARSETS[charset]
        self.charset_name: str = charset
    

    def colorize(self, text: str, fgcolor: Color = None, bgcolor: Color = None,
                 attrs: Iterable[Attribute] = None, color_mode: int = None,
                 *, 
                 no_color: Optional[bool] = None,
                 force_color: Optional[bool] = None) -> str:
        """ 
        ### Colorize
        Colorize the `text` using the color mode specified by `color_mode`.
        Uses module level `COLORMODE` if `color_mode` is `None`.

        This method uses `ansy.colored()`.

        #### ARGS:
        - `text`: the text to colorize
        - `fgcolor`: foreground color
        - `bgcolor`: background color
        - `attrs`: attributes list
        - `color_mode`: color mode

        This method sets `fgcolor` and `bgcolor` to `None` if the
        module-level `USE_COLORS` is set to False.

        ```
        # Example
        >> from pinsy import Pins
        >> pins = Pins()
        >>
        >> text = 'Hello, World!'
        >> pins.colorize(text, 'red', 'black', ['bold', 'blink'])
        >>
        >> pins.colorize(text, 'plum', color_mode=8)  # 8-bit color: name
        >> pins.colorize(text, 215, color_mode=8) # 8-bit color: code
        >>
        >> pins.colorize(text, '#B00B1E', color_mode=24) # 24-bit color: Hex
        >> pins.colorize(text, (255,100,100), color_mode=24) # 24-bit color: RGB
        ```

        Raises `ColorModeError` if:
        - `color_mode` is invalid

        Raises `InvalidColorError` if:
        - `fgcolor` is invalid
        - `bgcolor` is invalid

        Raises `AssertionError` if:
        - `attrs` is not a list or tuple

        Raises `AttributeError` if:
        - `attrs` contains an invalid attribute
        """
        if not text:
            return ""

        if attrs:
            assert isinstance(attrs, (tuple, list)), \
                "attrs must be a list or tuple"

        color_mode = color_mode if color_mode else self.COLORMODE
        no_color = no_color if no_color else not self.USE_COLORS
        
        return colored(text, fgcolor, bgcolor, attrs, color_mode,
                       no_color=no_color, force_color=force_color)

    def colorize_regex(self, text: str,
                       pattern: Union[Pattern, str],
                       fgcolor: Color = None,
                       bgcolor: Color = None,
                       attrs: Iterable[Attribute] = None) -> str:
        """ 
        ### Colorize Regex
        Colorize all matches of `pattern` found in `text`.

        #### ARGS:
        - `text`: the text to find the substring in
        - `pattern`: the regex pattern to match for (accepts compiled patterns as well)
        - `fgcolor`: the foreground color of matches
        - `bgcolor`: the background color of matches
        - `attrs`: the attributes list

        ```
        # Example
        >> pattern = "8008135"
        >> pins.colorize_regex("8008135 is a number", pattern, fgcolor="red")
        '8008135 is a number' # 8008135 is colored red
        ..
        >> import re
        >> pattern = re.compile(r"[0-9]+")
        >> pins.colorize_regex("8008135 is a number", pattern, fgcolor="red")
        '8008135 is a number' # every digit is colored red
        ```

        Raises `AssertionError` if:
        - `text` is not a string
        - `attrs` is not a tuple or list

        Raises `AttributeError` if:
        - `attrs` contains an invalid attribute

        Raises `InvalidColorError` if:
        - `fgcolor` is unrecognized
        - `bgcolor` is unrecognized
        """
        assert isinstance(text, str), "text is not a str"
        if not text:
            return text

        self._validate_attrs([('attrs', attrs)])

        ansi_fmt = self.create_ansi_fmt(fgcolor, bgcolor, attrs)

        # Colorizes the match
        def colorize_match_(m):
            return ansi_fmt % m.group(0)

        return re.sub(pattern, colorize_match_, text)

    def inputc(self, prompt: object = "",
               prompt_fg: Color = None,
               prompt_bg: Color = None,
               prompt_attrs: Iterable[Attribute] = None,
               input_fg: Color = None,
               input_bg: Color = None,
               input_attrs: Iterable[Attribute] = None) -> str:
        """ 
        ### Colored Input
        Python's `input()` with color support. All three color modes are supported.

        ##### NOTE:
        This method is not a replacement for the built-in `input()`.
        Although, It's not drastically slow, It should only be used
        when you need color support.

        #### ARGS:
        - `prompt`: prompt message
        - `prompt_fg`: foreground color of prompt message (default is `None`)
        - `prompt_bg`: background color of prompt message (default is `None`)
        - `prompt_attrs`: attributes of prompt message (default is `None`)
        - `input_fg`: foreground color of input that user types (default is `None`)
        - `input_bg`: background color of input that user types (default is `None`)
        - `input_attrs`: attributes of input that user types (default is `None`)

        ```
        # Example
        >> pins.inputc('Type something: ', input_fg='light_red')
        .. Type something: hello, there!
        'hello, there!'
        ```

        Raises all exceptions raised by `ansy` and `Pins.olorize`
        """
        # Create ANSI to format user-input
        input_ansi = self._make_ansi(input_fg, input_bg, input_attrs,
                                     self.COLORMODE)

        std = sys.stdout
        try:
            std.write(self.colorize(str(prompt), prompt_fg, prompt_bg,
                                    prompt_attrs))
            if input_ansi:
                std.write(input_ansi)
            std.flush()
            return input()

        finally:
            # Reset before returning
            std.write(ANSI_CODES['reset'])
            std.flush()

    def input_multiline(self, prompt: str = '', stop_word: str = '',
                        ignore_newlines: bool = False,
                        prompt_fg: Color = None,
                        prompt_bg: Color = None,
                        prompt_attrs: Iterable[Attribute] = None,
                        input_fg: Color = None,
                        input_bg: Color = None,
                        input_attrs: Iterable[Attribute] = None) -> str:
        """
        ### Input Multiline
        Take multiline input from user.

        #### ARGS:
        - `prompt`: prompt message
        - `stop_word`: stop taking inputs when encountered just these chars on a line.
        - `ignore_newlines`: whether to include newlines in return string or ignore.
        - `prompt_fg`: foreground color of prompt message (default is `None`)
        - `prompt_bg`: background color of prompt message (default is `None`)
        - `prompt_attrs`: attributes of prompt message (default is `None`)
        - `input_fg`: foreground color of input that user types (default is `None`)
        - `input_bg`: background color of input that user types (default is `None`)
        - `input_attrs`: attributes of input that user types (default is `None`)

        ```
        # Example
        >> pins.input_multiline("Enter a paragraph: ", stop_word='done')
        .. >> Enter a paragraph: Lorem ipsum dolor sit amet consectetur, adipisicing elit.
        At ab quidem itaque mollitia dolorum expedita.
        'Lorem ipsum dolor sit amet consectetur, adipisicing elit.\\nAt ab quidem itaque mollitia dolorum expedita.'
        ```
        """
        stop_word = stop_word.lower()
        print(self.promptize(prompt, prompt_fg, prompt_bg, prompt_attrs), end='')
        userinput = ""
        newline = " " if ignore_newlines else "\n"
        while True:
            tmp = self.inputc(input_fg=input_fg,
                              input_bg=input_bg,
                              input_attrs=input_attrs)
            if tmp.strip().lower() == stop_word:
                return userinput
            userinput += tmp + newline

    def input_int(self, prompt: str = '',
                  min_: int = None, max_: int = None,
                  prompt_color: Color = None,
                  prompt_attrs: Iterable[Attribute] = None,
                  input_color: Color = None,
                  input_attrs: Iterable[Attribute] = None) -> int:
        """ 
        ### Input Int
        Asks user for input, accepts integers only within the constaints.
        Returns an `int`. asks agains upon invalid inputs and keeps asking until a
        valid integer entered or `KeyboardInterrupt`.

        #### ARGS:
        - `prompt`: prompt message
        - `min_`: minimum accepted integer (`None` removes minimum constraint)
        - `max_`: maximum accepted integer (`None` removes maximum constraint)
        - `prompt_color`: foreground color of prompt message (`None` uses the default color)
        - `prompt_attrs`: attributes for prompt message (default is `None`)
        - `input_color`: foreground color of input that user types (`None` uses the default terminal color)
        - `input_attrs`: attributes for input that user types (default is `None`)

        ```
        # Example
        >> pins.input_int()
        .. >> Enter an integer: 25
        25
        ```
        Raises `ValueError` if:
        - `min_` is greater than `max_`
        """
        if (min_ != None and max_ != None) and min_ > max_:
            raise ValueError("min_ cannot be greater than max_")

        self._validate_colors([("prompt_color", prompt_color)])

        prompt = prompt if prompt else "Enter an integer: "
        prompt = self.promptize(prompt)
        try:
            while True:
                try:
                    i = int(self.inputc(prompt, prompt_fg=prompt_color,
                                        prompt_attrs=prompt_attrs,
                                        input_fg=input_color,
                                        input_attrs=input_attrs))
                except ValueError:
                    self.print_error("Only integers accepted.")
                    continue

                # Range Validation
                if min_ != None and i < min_:
                    self.print_error(f"integer must be atleast {min_}")
                    continue
                if max_ != None and i > max_:
                    self.print_error(f"integer must be atmost {max_}")
                    continue

                return i
        except (KeyboardInterrupt, EOFError):
            if self.handle_errors == "callback":
                self.error_callback()
            elif self.handle_errors == "raise":
                raise

            # Exit for `quit`
            sys.exit(1)

    def input_float(self, prompt: str = '', min_: float = None, max_: float = None,
                    prompt_color: Color = None, prompt_attrs: Iterable[Attribute] = None,
                    input_color: Color = None, input_attrs: Iterable[Attribute] = None) -> float:
        """ 
        ### Input Float
        Asks user for input, accepts Floats (and integers) within the constaints.
        Returns an `float`. asks agains upon invalid inputs and keeps asking until a
        valid float entered or `KeyboardInterrupt`.

        #### ARGS:
        - `prompt`: prompt message
        - `min_`: minimum accepted float (`None` removes minimum constraint)
        - `max_`: maximum accepted float (`None` removes maximum constraint)
        - `prompt_color`: foreground color of prompt message (`None` uses the default color)
        - `prompt_attrs`: attributes for prompt message (default is `None`)
        - `input_color`: foreground color of input that user types (`None` uses the default terminal color)
        - `input_attrs`: attributes for input that user types (default is `None`)

        ```
        # Example
        >> pins.input_float()
        .. >> Enter an float: 2.5
        2.5
        ```

        Raises `ValueError` if:
        - `min_` is greater than `max_`
        """
        if (min_ != None and max_ != None) and min_ > max_:
            raise ValueError("'min_' cannot be greater than 'max_'")

        self._validate_colors([("prompt_color", prompt_color)])

        prompt = prompt if prompt else "Enter a float: "
        prompt = self.promptize(prompt)
        try:
            while True:
                try:
                    i = float(self.inputc(prompt, prompt_fg=prompt_color,
                                          prompt_attrs=prompt_attrs,
                                          input_fg=input_color,
                                          input_attrs=input_attrs))
                except ValueError:
                    self.print_error("Only numbers accepted.")
                    continue

                # Range Validation
                if min_ != None and i < min_:
                    self.print_error(f"float must be atleast {min_}")
                    continue
                if max_ != None and i > max_:
                    self.print_error(f"float must be atmost {max_}")
                    continue

                return i
        except (KeyboardInterrupt, EOFError):
            if self.handle_errors == "callback":
                self.error_callback()
            elif self.handle_errors == "raise":
                raise

            # Exit for `quit`
            sys.exit(1)

    def input_str(self, prompt: str = '', empty_allowed: bool = False,
                  constraint: Union[StrConstraint, str, None] = None,
                  min_length: int = None, max_length: int = None,
                  prompt_color: Color = None,
                  prompt_attrs: Iterable[Attribute] = None,
                  input_color: Color = None,
                  input_attrs: Iterable[Attribute] = None) -> str:
        """ 
        ### Input Str
        Asks user for input, accepts strings within the constaints.
        Returns an `str`. asks agains upon invalid inputs and keeps asking until a
        valid `str` entered or `KeyboardInterrupt`.

        #### ARGS:
        - `prompt`: prompt message
        - `empty_allowed`: whether to allow empty inputs (`True` allows empty inputs)
        - `constraint`: set a constraint to accept only a specific set of characters.
            - `only_alpha`: only alphabets allowed
            - `only_digits`: only digits allowed
            - `only_alnum`: only alphanumerics allowed
            - `None`: all characters allowed
        - `min_length`: minimum length of input (`None` removes minimum constraint)
        - `max_length`: maximum length of input (`None` removes maximum constraint)
        - `prompt_color`: foreground color of prompt message (`None` uses the default color)
        - `prompt_attrs`: attributes for prompt message (default is `None`)
        - `input_color`: foreground color of input that user types (`None` uses the default terminal color)
        - `input_attrs`: attributes for input that user types (default is `None`)

        ```
        # Example
        >> pins.input_str()
        .. >> Enter an string: this is a string
        'this is a string'
        ```

        Raises a `AssertionError` if:
        - `constraint` is not a `str`
        - `constraint` is invalid

        Raises `ValueError` if:
        - `min_length` is greater than max_length
        """
        # Constraint validations
        if constraint:
            assert isinstance(constraint, str), "constraint must be a string."
            assert constraint in CONSTRAINTS, f"Invalid constraint: '{constraint}'"

        # Minlength, MaxLength validation
        if (min_length != None and max_length != None) and min_length > max_length:
            raise ValueError("min_length cannot be greater than max_length")

        self._validate_colors([("prompt_color", prompt_color)])

        prompt = prompt if prompt else "Enter a string: "
        prompt = self.promptize(prompt)
        try:
            while True:
                inp = self.inputc(prompt, prompt_fg=prompt_color,
                                  prompt_attrs=prompt_attrs,
                                  input_fg=input_color,
                                  input_attrs=input_attrs)
                if not empty_allowed and not inp:
                    # If empty not allowed and input is empty
                    self.print_error("Field cannot be empty.")
                    continue

                # Length Validation
                if min_length != None and len(inp) < min_length:
                    self.print_error(f"input must be atleast {
                                     min_length} characters long.")
                    continue
                if max_length != None and len(inp) > max_length:
                    self.print_error(f"input must be atmost {
                                     max_length} characters long.")
                    continue

                if inp:
                    if constraint == "only_alpha" and not inp.isalpha():
                        self.print_error("Only alphabets are allowed.")
                        continue

                    elif constraint == "only_digits" and not inp.isdigit():
                        self.print_error("Only digits are allowed.")
                        continue

                    elif constraint == "only_alnum" and not inp.isalnum():
                        self.print_error(
                            "Only alphabets and digits are allowed.")
                        continue

                return inp

        except (KeyboardInterrupt, EOFError):
            if self.handle_errors == "callback":
                self.error_callback()
            elif self.handle_errors == "raise":
                raise

            # Exit for `quit`
            sys.exit(1)

    def input_question(self, prompt: str = '', prompt_color: Color = None,
                       prompt_attrs: Iterable[Attribute] = None,
                       input_color: Color = None,
                       input_attrs: Iterable[Attribute] = None) -> bool:
        """ 
        ### Input Question
        Asks user a question, accepts `y` or `n` only. Returns `True`
        for `y` and `False` for `n`. Asks agains upon invalid inputs 
        and keeps asking until a valid answer entered or `KeyboardInterrupt`.

        #### ARGS:
        - `prompt`: prompt message
        - `prompt_color`: foreground color of prompt message (`None` uses the default color)
        - `prompt_attrs`: attributes for prompt message (default is `None`)
        - `input_color`: foreground color of input that user types (`None` uses the default terminal color)
        - `input_attrs`: attributes for input that user types (default is `None`)

        ```
        # Example
        >> pins.input_question()
        .. >> Do you agree? (y/N): y
        True 
        ```

        """
        self._validate_colors([("prompt_color", prompt_color)])

        prompt = prompt if prompt else "Do you agree? (y/N): "
        prompt = self.promptize(prompt)
        try:
            while True:
                u = self.inputc(prompt, prompt_fg=prompt_color,
                                prompt_attrs=prompt_attrs,
                                input_fg=input_color,
                                input_attrs=input_attrs).lower()
                if u == "y":
                    return True
                elif u == "n":
                    return False
                else:
                    self.print_error("Only 'y' or 'n' is accepted.")
        except (KeyboardInterrupt, EOFError):
            if self.handle_errors == "callback":
                self.error_callback()
            elif self.handle_errors == "raise":
                raise

            # Exit for `quit`
            sys.exit(1)

    def input_email(self, prompt: str = '', prompt_color: Color = None,
                    prompt_attrs: Iterable[Attribute] = None,
                    input_color: Color = None,
                    input_attrs: Iterable[Attribute] = None) -> str:
        """ 
        ### Input Email
        Asks user for input, accepts emails only.
        Returns a `str`. Asks agains upon invalid inputs 
        and keeps asking until a valid email entered or `KeyboardInterrupt`.

        Email is matched with a simplified version of a regex (regular expression)
        pattern that most browsers nowadays use to validate email addresses
        in the web forms.

        #### ARGS:
        - `prompt`: prompt message
        - `prompt_color`: foreground color of prompt message (`None` uses the default color)
        - `prompt_attrs`: attributes for prompt message (default is `None`)
        - `input_color`: foreground color of input that user types (`None` uses the default terminal color)
        - `input_attrs`: attributes for input that user types (default is `None`)

        ```
        # Example
        >> pins.input_email()
        .. >> Enter email: pins@python.com
        'pins@python.com'
        ```

        """
        self._validate_colors([("prompt_color", prompt_color)])

        prompt = prompt if prompt else "Enter email: "
        prompt = self.promptize(prompt)
        try:
            while True:
                e = self.inputc(prompt, prompt_fg=prompt_color,
                                prompt_attrs=prompt_attrs,
                                input_fg=input_color,
                                input_attrs=input_attrs)
                if not e:
                    self.print_error("Email cannot be empty.")
                    continue

                # Match regex pattern
                if Validator.is_valid_email(e):
                    return e

                self.print_error(f"Invalid email: '{e}'")

        except (KeyboardInterrupt, EOFError):
            if self.handle_errors == "callback":
                self.error_callback()
            elif self.handle_errors == "raise":
                raise

            # Exit for `quit`
            sys.exit(1)

    @typecheck(only=['prompt', 'custom_regex', 'custom_regex_error'])
    def input_password(self, prompt: str = '',
                       confirm: bool = False,
                       require_strong: bool = False,
                       custom_regex: Union[Pattern, str, None] = None,
                       custom_regex_error: str = '',
                       prompt_color: Color = None,
                       prompt_attrs: Iterable[Attribute] = None) -> str:
        """ 
        ### Input password
        Asks user for input, accepts password `str`.
        Returns a `str`. Asks agains upon invalid inputs 
        and keeps asking until a valid password entered or `KeyboardInterrupt`.

        #### ARGS:
        - `prompt`: prompt message
        - `confirm`: confirm password by asking again.
        - `require_strong`: accepts only strong passwords
            A password is strong if:
            - contains atleast one lowercase letter.
            - contains atleast one uppercase letter.
            - contains atleast one special character. ``'"~!@#$%^&*()_-+=`
            - contains is atleast one digit.
            - its length is atleast 8.
        - `custom_regex`: accept passwords only if they match this pattern. (set `require_strong` to `False` to avoid collisions)
        - `custom_regex_error`: the message to print when custom regex doesn't match
        - `prompt_color`: foreground color of prompt message (`None` uses the default color)
        - `prompt_attrs`: attributes for prompt message (default is `None`)

        (by default, `constraint` is set to `''` meaning every character is allowed.)

        ```
        # Example
        >> pins.input_password()
        .. >> Enter password (hidden on purpose): 
        'root'
        ```
        """
        self._validate_colors([("prompt_color", prompt_color)])

        prompt = prompt if prompt else "Enter password (hidden on purpose): "
        custom_regex_error = custom_regex_error if custom_regex_error else "Invalid password, try again!"
        prompt = self.promptize(prompt, prompt_color, attrs=prompt_attrs)
        prompt_confirm = self.promptize("Confirm password: ",prompt_color,
                                        attrs=prompt_attrs)
        try:
            while True:
                p = getpass(prompt)
                if not p:
                    self.print_error("Password cannot be empty.")
                    continue

                if require_strong and not Validator.is_strong_password(p):
                    self.print_error(
                        """Password must have length between 8-500 and must contain atleast one lowercase letter, one uppercase letter, one digit and one special character.""")
                    continue
                
                if custom_regex and not re.fullmatch(custom_regex, p):
                    self.print_error(custom_regex_error)
                    continue

                # Confirm
                if confirm and (getpass(prompt_confirm) != p):
                    self.print_error("Passwords did not match.")
                    continue

                return p
        except (KeyboardInterrupt, EOFError):
            if self.handle_errors == "callback":
                self.error_callback()
            elif self.handle_errors == "raise":
                raise

            # Exit for `quit`
            sys.exit(1)

    @typecheck(only=['prompt', 'extension', 'max_length'])
    def input_file(self, prompt: str = '',
                   extension: Optional[str] = "*",
                   max_length: int = 250,
                   must_exist: bool = True,
                   prompt_color: Color = None,
                   prompt_attrs: Iterable[Attribute] = None,
                   input_color: Color = None,
                   input_attrs: Iterable[Attribute] = None) -> str:
        """ 
        ### Input File
        Asks user for input, accepts filepaths only within the constraints.
        Returns a `str`. Asks agains upon invalid inputs 
        and keeps asking until a valid filepath entered or `KeyboardInterrupt`.

        #### ARGS:
        - `prompt`: prompt message
        - `extension`: only accept a file with a specific extension. (e.g. `.py`, `.txt`)
            - `*`: accept files with any extension
            - `None`: accept files with/without any extension
        - `max_length`: maximum length of the filepath (exluding slashes, extension and drive)
        - `must_exist`: file must exist (default to `True`)
        - `prompt_color`: foreground color of prompt message (`None` uses the default color)
        - `prompt_attrs`: attributes for prompt message (default is `None`)
        - `input_color`: foreground color of input that user types (`None` uses the default terminal color)
        - `input_attrs`: attributes for input that user types (default is `None`)

        `extension` must be provided with `.` (e.g `.py` or `.txt` etc)

        ```
        # Example
        >> pins.input_file()
        .. >> Enter a filepath: somefolder/somefile.txt
        'somefolder/somefile.txt'
        ```

        Raises `AssertionError` if:
        - `extension` is an empty string

        Raises `ValueError` if:
        - `extension` does not startswith `.` (except `*`)
        """
        assert extension != "", "extension cannot be empty."

        if extension != None and (extension != "*" and not extension.startswith(".")):
            raise ValueError("extension must start with a period ('.').")

        self._validate_colors([("prompt_color", prompt_color)])

        prompt = prompt if prompt else "Enter a filepath: "
        prompt = self.promptize(prompt)
        try:
            while True:
                filepath = self.inputc(prompt, prompt_fg=prompt_color,
                                       prompt_attrs=prompt_attrs,
                                       input_fg=input_color,
                                       input_attrs=input_attrs)

                is_valid = Validator.is_valid_filepath(filepath, extension,
                                                       max_length)
                if is_valid != True:
                    self.print_error(is_valid)
                    continue

                # Exist or not?
                if must_exist and not isfile(filepath):
                    self.print_error(f"File does not exist: '{filepath}'")
                    continue

                return filepath

        except (KeyboardInterrupt, EOFError):
            if self.handle_errors == "callback":
                self.error_callback()
            elif self.handle_errors == "raise":
                raise

            # Exit for `quit`
            sys.exit(1)

    def input_dir(self, prompt: str = '', max_length: int = 250, must_exist: bool = True,
                  prompt_color: Color = None, prompt_attrs: Iterable[Attribute] = None,
                  input_color: Color = None, input_attrs: Iterable[Attribute] = None) -> str:
        """ 
        ### Input Directory
        Asks user for input, accepts directory paths only.
        Returns a `str`. Asks agains upon invalid inputs 
        and keeps asking until a valid filepath entered or `KeyboardInterrupt`.

        #### ARGS:
        - `prompt`: prompt message
        - `max_length`: maximum length of the filepath (exluding slashes and drive)
        - `must_exist`: directory must exist (default to `True`)
        - `prompt_color`: foreground color of prompt message (`None` uses the default color)
        - `prompt_attrs`: attributes for prompt message (default is `None`)
        - `input_color`: foreground color of input that user types (`None` uses the default terminal color)
        - `input_attrs`: attributes for input that user types (default is `None`)

        ```
        # Example
        >> pins.input_dir()
        .. >> Enter path to a directory: somefolder/anotherfolder
        'somefolder/anotherfolder'
        ```

        """
        self._validate_colors([("prompt_color", prompt_color)])

        prompt = prompt if prompt else "Enter path to a directory: "
        prompt = self.promptize(prompt)
        try:
            while True:
                directory = self.inputc(prompt, prompt_fg=prompt_color,
                                        prompt_attrs=prompt_attrs,
                                        input_fg=input_color,
                                        input_attrs=input_attrs)

                is_valid = Validator.is_valid_dirpath(directory, max_length)
                if is_valid != True:
                    self.print_error(is_valid)
                    continue

                # # Directory MUST exist (if required).
                if must_exist and not isdir(directory):
                    self.print_error(
                        f"Directory '{directory}' does not exist.")
                    continue

                # Safe to return the directory
                return normpath(directory)

        except (KeyboardInterrupt, EOFError):
            if self.handle_errors == "callback":
                self.error_callback()
            elif self.handle_errors == "raise":
                raise

            # Exit for `quit`
            sys.exit(1)

    def input_ip(self, prompt: str = '', version: int = 4,
                 prompt_color: Color = None,
                 prompt_attrs: Iterable[Attribute] = None,
                 input_color: Color = None,
                 input_attrs: Iterable[Attribute] = None) -> str:
        """ 
        ### Input IP Address
        Asks user for IP Address and keeps asking until a valid
        ip address is entered or `KeyboardInterrupt`.

        #### ARGS:
        - `prompt`: prompt message
        - `version`: version of ip address (version `4` or `6`)
        - `prompt_color`: foreground color of prompt message (`None` uses the default color)
        - `prompt_attrs`: attributes for prompt message (default is `None`)
        - `input_color`: foreground color of input that user types (`None` uses the default terminal color)
        - `input_attrs`: attributes for input that user types (default is `None`)

        ```
        # Example
        >> pins.input_ip()
        .. >> Enter IPv4 Address: 192.168.0.1
        '192.168.0.1'
        ..
        >> pins.input_ip(version=6)
        .. >> Enter IPv6 Address: 2001:db8:85a3::8a2e:370:7334
        '2001:db8:85a3::8a2e:370:7334'
        ```

        Raises `AssertionError` if:
        - `version` is not 4 or 6

        """
        assert version in {4, 6}, "version must be 4 or 6."

        self._validate_colors([("prompt_color", prompt_color)])

        prompt = prompt if prompt else f"Enter IPv{version} Address: "
        prompt = self.promptize(prompt)
        try:
            while True:
                ip = self.inputc(prompt, prompt_fg=prompt_color,
                                 prompt_attrs=prompt_attrs,
                                 input_fg=input_color,
                                 input_attrs=input_attrs)
                if not ip:
                    self.print_error("IP Address cannot be empty.")
                    continue

                if Validator.is_valid_ip(ip, version):
                    return ip

                self.print_error(f"Invalid IPv{version} Address: '{ip}'")

        except (KeyboardInterrupt, EOFError):
            if self.handle_errors == "callback":
                self.error_callback()
            elif self.handle_errors == "raise":
                raise

            # Exit for `quit`
            sys.exit(1)

    def input_url(self, prompt: str = '',
                  prompt_color: Color = None,
                  prompt_attrs: Iterable[Attribute] = None,
                  input_color: Color = None,
                  input_attrs: Iterable[Attribute] = None) -> str:
        """ 
        ### Input URL
        Asks user for a URL and keeps asking until a valid
        url is entered or `KeyboardInterrupt`.

        #### ARGS:
        - `prompt`: prompt message
        - `prompt_color`: foreground color of prompt message (`None` uses the default color)
        - `prompt_attrs`: attributes for prompt message (default is `None`)
        - `input_color`: foreground color of input that user types (`None` uses the default terminal color)
        - `input_attrs`: attributes for input that user types (default is `None`)

        ```
        # Example
        >> pins.input_url()
        .. >> Enter URL: https://github.com/Anas-Shakeel
        'https://github.com/Anas-Shakeel'
        ```
        """
        self._validate_colors([("prompt_color", prompt_color)])

        prompt = prompt if prompt else "Enter URL: "
        prompt = self.promptize(prompt)
        try:
            while True:
                url = self.inputc(prompt, prompt_fg=prompt_color,
                                  prompt_attrs=prompt_attrs,
                                  input_fg=input_color,
                                  input_attrs=input_attrs)
                if not url:
                    self.print_error("URL cannot be empty.")
                    continue

                if Validator.is_valid_url(url):
                    return url

                self.print_error(f"Invalid URL: '{url}'")

        except (KeyboardInterrupt, EOFError):
            if self.handle_errors == "callback":
                self.error_callback()
            elif self.handle_errors == "raise":
                raise

            # Exit for `quit`
            sys.exit(1)

    def input_menu(self, options: list,
                   bullet: Bullet = ">",
                   bullet_fg: Color = None,
                   bullet_bg: Color = None,
                   bullet_attrs: Iterable[Attribute] = None,
                   selected_fg: Color = None,
                   selected_bg: Color = None,
                   selected_attrs: Iterable[Attribute] = None,
                   normal_fg: Color = None,
                   normal_bg: Color = None,
                   normal_attrs: Iterable[Attribute] = None) -> int:
        """ 
        ### Input Menu
        Lets users select an item from a menu (using Up/Down arrow keys) 
        and returns the selection as number (`index + 1`).

        #### NOTE:
        CTRL+C (`KeyboardInterrupt`) cannot be read with this method,
        so `Enter` key is the only way to proceed.

        #### ARGS:
        - `options`: the menu items (list of strings)
        - `bullet`: the bullet character (following the selected option)
        - `bullet_fg`: foreground color of bullet char(s)
        - `bullet_bg`: background color of bullet char(s)
        - `bullet_attrs`: attributes for bullet char(s)
        - `selected_fg`: foreground color of selected option
        - `selected_bg`: background color of selected option
        - `selected_attrs`: attributes for selected option
        - `normal_fg`: foreground color of normal options
        - `normal_bg`: background color of normal options
        - `normal_attrs`: attributes for normal options

        ```
        # Example
        >> menu = ['Python', 'C', 'Rust']
        >> pins.input(menu)
        ..   Python
        .. > C
        ..   Rust
        2
        ```

        Raises `AssertionError` if
        - `options` is not a list
        - `bullet` is not a string

        Raises all exceptions that `ansy` would raise for 
        invalid colors and attributes.
        """
        assert type(options) == list, "options is expected to be a list"
        assert type(bullet) == str, "bullet is expected to be a str"

        # Ansi formatting
        bullet = self.colorize(bullet, bullet_fg, bullet_bg, bullet_attrs)
        selected_ansi = self._make_ansi(selected_fg, selected_bg, selected_attrs,
                                        color_mode=self.COLORMODE)
        normal_ansi = self._make_ansi(normal_fg, normal_bg, normal_attrs,
                                      color_mode=self.COLORMODE)

        total_options = len(options)
        selected_index = 0

        with HiddenCursor():
            # Move cursor total_options lines down first
            print("\n"*total_options, end='', flush=True)

            while True:
                utils.clear_lines_above(total_options)
                self._render_menu(options, selected_index, bullet,
                                  selected_ansi, normal_ansi)

                # Wait for a keypress
                key = utils.read_key()

                if key == utils.UP and selected_index > 0: # UP
                    selected_index -= 1
                elif key == utils.DOWN and selected_index < total_options - 1: # DOWN
                    selected_index += 1
                elif key == '\r': # ENTER
                    return selected_index + 1

    def print_error(self, error: str, quit_too: bool = False):
        """ 
        ### Print error
        Prints a formatted version of `error`. Closes the application
        with an exit status `1` if `quit_too` is set to `True`.

        #### ARGS:
        - `error`: the error message to print
        - `quit_too`: quit the application after printing the error (Defualt to `False`)

        ```
        # Example
        >> pins.print_error("This is error")
        █ Error: This is error
        ```

        """
        print(self.create_status("Error", str(error),
                                 label_fg=self.DEFAULT_COLORS['error'],
                                 label_attrs=['bold'], text_attrs=['italic']))

        if quit_too:
            exit(1)

    def print_info(self, info: str):
        """ 
        ### Print info
        Prints a formatted version of `info`.

        #### ARGS:
        - `info`: the info message to print

        ```
        # Example
        >> pins.print_info("This is info")
        █ Info: This is info
        ```

        """
        print(self.create_status("Info", str(info),
                                 label_fg=self.DEFAULT_COLORS['info'],
                                 label_attrs=['bold'], text_attrs=['italic']))

    def print_warning(self, warning: str):
        """ 
        ### Print Warning
        Prints a formatted version of `warning`.

        #### ARGS:
        - `warning`: the warning message to print

        ```
        # Example
        >> pins.print_warning("This is warning")
        █ Warning: This is warning
        ```
        """
        print(self.create_status("Warning", str(warning),
                                 label_fg=self.DEFAULT_COLORS['warn'],
                                 label_attrs=['bold'], text_attrs=['italic']))

    def print_success(self, success: str):
        """ 
        ### Print Warning
        Prints a formatted version of `success`.

        #### ARGS:
        - `success`: the success message to print

        ```
        # Example
        >> pins.print_success("This is success")
        █ Success: This is success
        ```
        """
        print(self.create_status("Success", str(success),
                                 label_fg=self.DEFAULT_COLORS['success'],
                                 label_attrs=['bold'], text_attrs=['italic']))

    def print_about(self, name: str = None,
                    version: str = None,
                    description: str = None,
                    author: str = None,
                    author_email: str = None,
                    source_url: str = None,
                    license: str = None,
                    platforms: list[str] | str = None,
                    *,
                    border_color: Color = None,
                    heading_fg: Color = None,
                    heading_bg: Color = None,
                    heading_attrs: Iterable[Attribute] = None,
                    keys_color: Color = None,
                    values_color: Color = None):
        """  
        ### Print About
        Print details of your program.

        #### ARGS:
        - `name`: name of the program
        - `version`: version of the program
        - `description`: short description of the program
        - `author`: author's name
        - `author_email`: author's email
        - `source_url`: project's source code url (e.g. `github.com/author/project`)
        - `license`: license of the project (e.g. `MIT` or `GNU`)
        - `platforms`: platforms supported by this program (e.g. `Windows` or `Unix`)
        - `border_color`: color of border
        - `heading_fg`: foreground color of heading
        - `heading_bg`: background color of heading
        - `heading_attrs`: attributes for heading
        - `keys_color`: color of keys
        - `values_color`: color of values

        """
        self._validate_types([
            ("name", name, (str, None)),
            ("version", version, (str, None)),
            ("description", description, (str, None)),
            ("author", author, (str, None)),
            ("author_email", author_email, (str, None)),
            ("source_url", source_url, (str, None)),
            ("license", license, (str, None)),
        ])

        if platforms:
            platforms = ", ".join(platforms) if isinstance(
                platforms, list) else platforms

        table = {
            "Name": name,
            "Version": version,
            "Description": description,
            "Author": author,
            "Author Email": author_email,
            "Source Url": source_url,
            "License": license,
            "Platforms": platforms,
        }

        # Is there anything in table except keys?
        if not any(table.values()):
            return

        # Create table
        heading = f"  About {name.title()}  " if name else None
        new_table = self.create_table(dictionary=table,
                                      heading=heading,
                                      heading_fg=heading_fg,
                                      heading_bg=heading_bg,
                                      heading_attrs=heading_attrs,
                                      keys_fg=keys_color,
                                      values_fg=values_color)

        # Create a box around table
        new_table = self.boxify(new_table,
                                wrap=False,
                                pad_x=6, pad_y=1,
                                y_align="center",
                                border_color=border_color)
        # Print the damn thing!
        print(new_table)

    def print_more(self, text: str, n: int = 1,
                   prompt: str = "",
                   prompt_align: XAlign = "left",
                   prompt_fg: Color = None,
                   prompt_bg: Color = None,
                   prompt_attrs: Iterable[Attribute] = None):
        """ 
        ### Print More
        Prints `text` in the terminal. when number of lines in `text` are more than
        number of visible lines in terminal (`terminal's height`), it adds a `MORE`
        prompt and shows next line upon `enter` keypress. `CTRL+C` to stop.

        #### ARGS:
        - `text`: text to print
        - `n`: number of lines to print after each `enter`
        - `prompt`: prompt message (e.g `---- MORE ----`)
        - `prompt_align`: prompt alignment (e.g `left`, `center`, `right`)
        - `prompt_fg`: foreground color of prompt
        - `prompt_bg`: background color of prompt
        - `prompt_attrs`: attributes of prompt

        ```
        >> pins.print_more(colors)
        #ffebee
        #ffcdd2
        #ef9a9a
        --snip--
        #e57373
        #ef5350
        ---- MORE ---- # Pressing enter would print next n lines
        ```

        Raises `AssertionError` if:
        - `n` is less than 1
        - `prompt` is not a string

        Raises all exceptions that `ansy` and `Pins.textalign_x` would raise for
        invalid inputs.
        """
        assert n > 0, "n must be greater than 0"
        assert type(prompt) == str, "prompt must be a string"

        w, h = get_terminal_size()
        prompt = prompt if prompt else "---- MORE ----"
        prompt = self.textalign_x(prompt, w, prompt_align)
        prompt = self.colorize(prompt, prompt_fg, prompt_bg, prompt_attrs)

        # Print first section
        lines = text.splitlines()
        stop_ = min(h-2, len(lines))
        print("\n".join(lines[:stop_]))

        # Print remaining lines
        with HiddenCursor():
            try:
                for batch in batched(lines[stop_:], n):
                    input(prompt)
                    utils.clear_lines_above(1)
                    print("\n".join(batch), flush=True)
            except KeyboardInterrupt:
                utils.clear_line()

    def print_pages(self, text: str, lines_per_page:int=10,
                    prompt: str = "",
                    prompt_fg: Color = None,
                    prompt_bg: Color = None,
                    prompt_attrs: Iterable[Attribute] = None):
        """
        ### Print Pages
        Prints paginated `text`. It prints a page, asks for keypress `enter` and
        then prints another page after removing the previous page. (`ctrl+c` to stop)

        This method uses `Batched` under the hood.

        #### ARGS:
        - `text`: text to paginate
        - `lines_per_page`: lines to show per page
        - `prompt`: prompt message (passed to `input()`)
        - `prompt_fg`: foreground color of prompt
        - `prompt_bg`: background color of prompt
        - `prompt_attrs`: attributes of prompt

        ```
        >> text = "line 1\\nline 2\\nline 3\\nline 4\\nline 5"
        >> p.print_pages(text, 2, "Enter to see next page...")
        line 1 
        line 2
        Enter to see next page...
        ```

        Raises `AssertionError` if:
        - `text` is not a string
        - `prompt` is not a string
        - `lines_per_page` is lesser than 1

        Raises all exceptions that `ansy` would raises for invalid inputs.
        """
        assert type(text) == str, \
            "text must be a string"

        assert lines_per_page > 0, \
            "lines_per_page cannot be lesser than 1"
        assert type(prompt) == str, \
            "prompt must be a string"

        prompt = self.colorize(
            f"\n{prompt}", prompt_fg, prompt_bg, prompt_attrs)
        newlines = max(prompt.count('\n')+1, 1)

        batches = Batched(text.splitlines(), lines_per_page)
        with HiddenCursor():
            for batch in batches.iterate():
                print("\n".join(batch), flush=True)

                if batches.has_next_batch:
                    try:
                        self.inputc(prompt, input_attrs=['concealed'])
                        utils.clear_lines_above(len(batch)+newlines)
                    except KeyboardInterrupt:
                        break
        utils.clear_line()

    def paginate(self, text: str, lines_per_page:int=10):
        """ 
        ### Paginate
        Paginates a multiline lengthy text. Returns a generator object which,
        yields a page on each iteration.
        A page is just a string of `lines_per_page` lines (or less).

        This method uses `Pins.Batched` class under the hood.

        #### ARGS:
        - `text`: text to paginate
        - `lines_per_page`: lines to show per page

        ```
        >> text = "line 1\\nline 2\\nline 3\\nline 4\\nline 5"
        >> for page in pins.paginate(length_text, 2):
        ..     print(page, end="\\n\\n")
        line 1
        line 2

        line 3
        line 4

        line 5
        ```

        Raises `AssertionError` if:
        - `text` is not str
        - `lines_per_page` is lesser than 1
        """
        assert type(text) == str, "text must be a string"
        assert lines_per_page > 0, "lines_per_page cannot be lesser than 1"

        with Batched(text.splitlines(), lines_per_page) as pages:
            for page in pages.iterate():
                yield "\n".join(page)

    def print_json(self, filepath: str, indent: int = 4,
                   quotes: bool = False,
                   str_color: Color = None,
                   number_color: Color = None,
                   keyword_color: Color = None,
                   key_color: Color = None,
                   symbol_color: Color = None,):
        """ 
        ### Print Json
        Pretty-print json with syntax highlighting. This method uses `Pins.JsonHighlight`

        #### ARGS:
        - `filepath`: the json filepath
        - `indent`: number of spaces to indent
        - `quotes`: remove the quotations (`""`)
        - `str_color`: color of string values
        - `number_color`: color of numeric values
        - `keyword_color`: color of keywords (`null`, `true`, `false` etc.)
        - `key_color`: color of object keys (`object` in json is `dict` in python)
        - `symbol_color`: color of symbols (`[,]{:}`)

        ```
        # Example
        >> pins.print_json("person.json")
        {
            "name": "anas",
            "age": "22",
            "hobbies": "coding, programming, writing code etc."
        }
        ```

        Raises `AssertionError` if:
        - `filepath` does not exist
        - `indent` is not an integer
        """
        assert isfile(filepath), "filepath does not exist."
        assert type(indent) == int, "indent must be an integer."

        if not self.USE_COLORS:
            str_color, number_color, symbol_color = None, None, None
            key_color, keyword_color = None, None

        with open(filepath, encoding="utf-8") as jfile:
            jdata = json.load(jfile)

        jsh = JsonHighlight(indent, quotes, self.COLORMODE,
                            str_color, number_color, keyword_color,
                            key_color, symbol_color)
        print(jsh.highlight(jdata))

    def typewrite(self, text: str, interval: float = 0.01, hide_cursor: bool = True):
        """ 
        ### Typewrite
        Print `text` in the terminal with a typewriter-like effect, where each
        character is "Written" (printed) with a short delay.

        This method uses `Pins.Typewriter` under the hood.

        #### ARGS:
        - `text`: the text to print
        - `interval`: interval between each character print.
        - `hide_cursor`: hide or show cursor

        ```
        >> pins.typewrite("write this.")
        write this.
        ```
        """
        w = Typewriter(interval)
        if hide_cursor:
            with HiddenCursor():
                w.write(text)
        else:
            w.write(text)

    def print_hr(self, width: int = None, pad_x: int = 0,
                 align: XAlign = "left", charset: Charset = None,
                 fill_char: FillChar = None, color: Color = None):
        """
        ### Print HR
        Prints the string returned from  `Pins.create_hr(args)` 

        ```
        # Example
        >> pins.print_hr(10, fill_char='-')
        ----------
        ```
        Raises all exceptions raised by `Pins.create_hr()`
        """
        print(self.create_hr(width, pad_x, align, charset, fill_char, color))

    @typecheck(skip=['color'])
    def create_hr(self, width: Optional[int] = None,
                  pad_x: int = 0,
                  align: Union[XAlign, str] = "left",
                  charset: Union[Charset, str, None] = None,
                  fill_char: Union[FillChar, str, None] = None,
                  color: Color = None):
        """ 
        ### Create Horizontal Rule (line)
        Creates a horizontal line in the terminal. Uses characters from `charset` if 
        set, otherwise uses the module level `charset`. `fill_char` takes
        precedence always.

        #### ARGS:
        - `width`: width of the line (default is `None` which takes terminal's width)
        - `pad_x`: padding on the x-axis (default is `0`)
        - `align`: alignment of the line (default is `left`)
            (alignments: `left`, `center`, `right`)
        - `charset`: character set to use in creating the line (default is `None` which uses the `charset` set as module level arg)
            - `ascii` `box` `box_rounded` `box_double` `box_heavy` `blocks`
        - `fill_char`: character to use to fill the line, overrides `charset` (default is `None` which uses the `charset`)
        - `color`: color of the line (default is `None`)

        ```
        >> # Example
        >> pins.create_hr(10, fill_char='+')
        '++++++++++'
        ```

        Raises `AssertionError` if:
        - `width` is not greater than 0
        - `charset` is invalid
        - `align` is not a valid alignment
        """
        assert width == None or width > 0, "width must be greater than 0"
        assert charset == None or charset in CHARSETS, f"Invalid charset: {charset}"
        assert align in ("center", "left", "right"), f"Invalid align: '{align}'"

        # Ensure padding is non-negative
        pad_x = max(pad_x, 0)

        terminal_width = get_terminal_size()[0]
        width = width if width else terminal_width

        charset = CHARSETS[charset] if charset else self.CHARSET
        fill_char = fill_char if fill_char else charset['NORMAL']
        hr = fill_char * (width - pad_x)

        if align == "center":
            hr = hr.center(terminal_width)
        elif align == "right":
            hr = hr.rjust(terminal_width)
        else:
            hr = hr.ljust(terminal_width)

        # Colorize the line
        return self.colorize(hr.rstrip(), color)

    def create_status(self, label: str, text: str,
                      label_fg: Color = None,
                      label_bg: Color = None,
                      label_attrs: Iterable[Attribute] = None,
                      text_fg: Color = None,
                      text_bg: Color = None,
                      text_attrs: Iterable[Attribute] = None):
        """ 
        ### Create Status
        Creates a formatted Status. Nicely handles newline characters.
        Returns a `str` status.

        #### ARGS:
        - `label`: the status label e.g `error, info, warning, success etc.`
        - `text`: the status text (after the status label)
        - `label_fg`: foreground color for the label (default is `None`)
        - `label_bg`: background color for the label (default is `None`)
        - `label_attrs`: attributes for the label (default is `None`)
        - `text_fg`: foreground color for the text (default is `None`)
        - `text_bg`: background color for the text (default is `None`)
        - `text_attrs`: attributes for the text (default is `None`)

        ```
        # Example
        >> pins.create_status("Hint", "this is a hint.")
        '█ Hint: this is a hint.'
        ```

        Raises `AssertionError` if:
        - `label` is not a `str`
        - `text` is not a `str`

        Raises `InvalidColorError` if:
        - `label_color` is unrecognized
        - `text_color` is unrecognized

        Raises `AttributeError` if:
        - `label_attr` contains an invalid attribute
        - `text_attr` contains an invalid attribute
        """
        # Type validation
        assert isinstance(label, str), "label must be a string."
        assert isinstance(text, str), "text must be a string."

        if not text or not label:
            return ""

        # Color validation
        if not self.USE_COLORS:
            label_fg, label_bg, text_fg, text_bg = None, None, None, None

        self._validate_attrs([('label_attrs', label_attrs),
                              ('text_attrs', text_attrs)])

        # Defining styles for colored_ansy func.
        style = {
            "bar": create_style(self.COLORMODE, label_fg, label_bg, label_attrs),
            "line": create_style(self.COLORMODE, text_fg, text_bg, text_attrs),
        }

        bar = self.STATUS_CHAR
        status_text = f"{bar} {label}: "
        indent = " "*(len(status_text) - 2)

        # Wrap the text
        max_width = get_terminal_size()[0] - len(status_text)
        text = fill(text, max_width, replace_whitespace=False)

        lines: list = text.splitlines()
        formatted_lines = ""
        for line in lines[1:]:
            formatted_lines += colored_ansy(f"@bar[{bar}] {indent}@line[{line}]\n",
                                            style)
        first_line = colored_ansy(f"@bar[{status_text}]@line[{lines[0]}]",
                                  style)

        if formatted_lines:
            first_line += "\n"

        # RETURN after Adding the status_text at the beginning
        return first_line + formatted_lines.rstrip("\n")

    def boxify(self, text: str,
               width: int = None,
               wrap: bool = False,
               replace_whitespace: bool = False,
               pad_x: int = 0, pad_y: int = 0,
               x_align: XAlign = "left",
               y_align: YAlign = "top",
               charset: Charset = None,
               border_color: Color = None,
               text_color: Color = None) -> str:
        """  
        ### Boxify
        Returns a formatted version of `text` in a box. This method uses
        `Pins.Box` under the hood.

        #### ARGS:
        - `text`: the text to boxify
        - `width`: width of the box
        - `wrap`: wrap the text
        - `replace_whitespace`: replace whitespaces with a single space.
        - `pad_x`: padding on X-axis
        - `pad_y`: padding on Y-axis
        - `x_align`: alignment of text on X-Axis (`left`, `center`, `right`)
        - `y_align`: alignment of text on Y-Axis (`top`, `center`, `bottom`)
        - `charset`: the charset to use (`None` uses module-level `CHARSET`)
        - `border_color`: color of the border
        - `text_color`: color of the text

        ```
        # Example
        >> pins.boxify("A Box", 20, x_align="center", charset="box_round")
        ╭──────────────────╮
        │      A Box       │
        ╰──────────────────╯
        ```
        Raises all exceptions that class `Boxify` would raise for invalid inputs.
        """
        if not self.USE_COLORS:
            text_color, border_color = None, None

        charset = charset if charset else self.charset_name
        box = Box(text, width, pad_x, pad_y, x_align, y_align, charset,
                  border_color, text_color, self.COLORMODE)

        return box.create(wrap=wrap, replace_whitespace=replace_whitespace)

    def print_list_ordered(self, items: list | Tuple,
                           indent: int = 0,
                           list_indent: int = 4,
                           line_height: int = 0,
                           num_color: Color = None,
                           num_attrs: Iterable[Attribute] = None,
                           item_color: Color = None,
                           item_attrs: Iterable[Attribute] = None):
        """
        ### Print List Ordered
        Prints the string returned from `create_list_ordered(args)`

        Raises all exceptions raised by `Pins.create_list_ordered()`
        """
        print(self.create_list_ordered(items=items,
                                       indent=indent,
                                       list_indent=list_indent,
                                       line_height=line_height,
                                       num_color=num_color,
                                       num_attrs=num_attrs,
                                       item_color=item_color,
                                       item_attrs=item_attrs))

    def print_list_unordered(self, items: list | Tuple,
                             bullet: Bullet = '+',
                             bullet_map: Iterable[Bullet] = None,
                             indent: int = 0,
                             list_indent: int = 4,
                             line_height: int = 0,
                             bullet_color: Color = None,
                             bullet_attrs: Iterable[Attribute] = None,
                             item_color: Color = None,
                             item_attrs: Iterable[Attribute] = None):
        """
        ### Print List Unordered
        Prints the string returned from `create_list_unordered(*args, **kwargs)`

        Raises all exceptions raised by `Pins.create_list_unordered()`
        """
        print(self.create_list_unordered(items=items,
                                         bullet=bullet,
                                         bullet_map=bullet_map,
                                         indent=indent,
                                         list_indent=list_indent,
                                         line_height=line_height,
                                         bullet_color=bullet_color,
                                         bullet_attrs=bullet_attrs,
                                         item_color=item_color,
                                         item_attrs=item_attrs))

    @typecheck(only=['items', 'indent', 'list_indent', 'line_height'])
    def create_list_ordered(self, items: Union[list, tuple],
                            indent: int = 0,
                            list_indent: int = 4,
                            line_height: int = 0,
                            num_color: Color = None,
                            num_attrs: Iterable[Attribute] = None,
                            item_color: Color = None,
                            item_attrs: Iterable[Attribute] = None):
        """  
        ### Create List Ordered
        Creates a numbered list from `items`. This method also supports nested lists.

        #### ARGS:
        - `items`: the items (iterable) to create list from
        - `indent`: number of characters to indent (from left)
        - `list_indent`: the indentation of each list in `items`
        - `line_height`: number of empty lines in between each text line
        - `num_color`: number's foreground color
        - `num_attrs`: number's attrs list
        - `item_color`: item's foreground color
        - `item_attrs`: item's attrs list

        ```
        # Example
        >> items = ['item 1', 'item 2', 'and so on.']
        >> pins.create_list_ordered(items)
        1. item 1
        2. item 2
        3. and so on.
        ```
        
        Raises `InvalidColorError` if:
        - `num_color` is invalid
        - `item_color` is invalid
        """

        if not items:
            return None

        # Create ansi format string
        num_fmt = self.create_ansi_fmt(num_color, None, num_attrs)
        item_fmt = self.create_ansi_fmt(item_color, None, item_attrs)

        newlines = '\n'*(max(line_height, 0) + 1)
        pad = ' '*indent

        # Create list
        return self._recurse_list(items=items,
                                  list_indent=list_indent,
                                  pad=pad,
                                  bullet="",
                                  prefix_fmt=num_fmt,
                                  item_fmt=item_fmt,
                                  list_type="ordered",
                                  newline=newlines)

    @typecheck(only=['items', 'indent', 'bullet', 'list_indent', 'line_height'])
    def create_list_unordered(self, items: Union[list, tuple],
                              bullet: Union[Bullet, str] = '+',
                              bullet_map: Iterable[Bullet] = None,
                              indent: int = 0,
                              list_indent: int = 4,
                              line_height: int = 0,
                              bullet_color: Color = None,
                              bullet_attrs: Iterable[Attribute] = None,
                              item_color: Color = None,
                              item_attrs: Iterable[Attribute] = None):
        """  
        ### Create List Unordered
        Creates an unordered list from `items`. This method also supports nested lists.

        #### ARGS:
        - `items`: the items (iterable) to create list from
        - `bullet`: the bullet character(s)
        - `bullet_map`: bullet characters for each level
        - `indent`: indentation of the whole list structure
        - `list_indent`: the indentation of each list in `items`
        - `line_height`: number of empty lines in between each text line
        - `bullet_color`: bullet's foreground color
        - `bullet_attrs`: bullet's attrs list
        - `item_color`: item's foreground color
        - `item_attrs`: item's attrs list

        ```
        # Example
        >> items = ['item 1', ['item 1.1', 'item 1.2'], 'item 2', 'and so on.']
        >> pins.create_list_unordered(items)
        + item 1
            + item 1.1
            + item 1.2
        + item 2
        + and so on.
        >> pins.create_list_unordered(items, bullet_map="+-")
        + item 1
            - item 1.1
            - item 1.2
        + item 2
        + and so on.
        ```

        Raises `InvalidColorError` if:
        - `bullet_color` is invalid
        - `item_color` is invalid
        """
        if not items:
            return None

        # Create Ansi Format Strings
        bullet_fmt = self.create_ansi_fmt(bullet_color, None, bullet_attrs)
        item_fmt = self.create_ansi_fmt(item_color, None, item_attrs)

        newlines = '\n'*(max(line_height, 0) + 1)
        pad = ' '*indent

        # Create list
        return self._recurse_list(items=items,
                                  list_indent=list_indent,
                                  pad=pad,
                                  bullet=bullet,
                                  bullet_map=bullet_map,
                                  prefix_fmt=bullet_fmt,
                                  item_fmt=item_fmt,
                                  list_type="unordered",
                                  newline=newlines)

    @typecheck(only=['dictionary', 'heading', 'indent_values', 'line_height'])
    def create_table(self, dictionary: dict,
                     heading: Optional[str] = None,
                     indent_values: int = 4,
                     line_height: int = 0,
                     ignore_none: bool = True,
                     heading_fg: Color = None,
                     heading_bg: Color = None,
                     heading_attrs: Iterable[Attribute] = None,
                     keys_fg: Color = None,
                     keys_bg: Color = None,
                     keys_attrs: Iterable[Attribute] = None,
                     values_fg: Color = None,
                     values_bg: Color = None,
                     values_attrs: Iterable[Attribute] = None):
        """ 
        ### Create Table
        Formats a dictionary as a table (sort of). This method does not
        colorize already colored text.

        #### ARGS:
        - `dictionary`: the dictionary to format as table
        - `heading`: the heading of the table
        - `indent_values`: number of spaces to indent the values
        - `line_height`: number of empty lines in between each text line
        - `ignore_none`: ignore keys with none values
        - `heading_fg`: foreground color of heading
        - `heading_bg`: background color of heading
        - `heading_attrs`: attributes of heading
        - `keys_fg`: foreground color of all the keys
        - `keys_bg`: background color of all the keys
        - `keys_attrs`: attributes for all the keys
        - `values_fg`: foreground color of all the values
        - `values_bg`: background color of all the values
        - `values_attrs`: attributes for all the values

        ```
        # Example
        >> items = {
        ..          'Name': 'Pins',
        ..          'Version': '1.0.0',
        ..          'Source': 'github.com/Anas-Shakeel/pinsy',
        .. }
        >> create_table(items)
        Name        Pins
        Version     1.0.0
        Source      github.com/Anas-Shakeel/pinsy
        ```
        """
        if not dictionary:
            return None

        key_ansi = self.create_ansi_fmt(keys_fg, keys_bg, keys_attrs)
        value_ansi = self.create_ansi_fmt(values_fg, values_bg, values_attrs)

        # Find the length of longest string in l1
        space: int = len(self._longest_string(dictionary.keys()))
        pad = " "*indent_values
        newlines: str = "\n"*(line_height+1)

        table = []
        for key, value in dictionary.items():
            if ignore_none and value == None:
                continue
            table.append(f"{key_ansi % key.ljust(space)} {
                         pad}{value_ansi % value}")
        table = newlines.join(table)

        # Add the heading if provided
        if heading:
            return "\n".join([self.colorize(heading, heading_fg, heading_bg, heading_attrs), " ", table])
        return table

    def promptize(self, prompt: str, fgcolor: Color = None, bgcolor: Color = None,
                  attrs: Iterable[Attribute] = None, prompt_char: str = None) -> str:
        """ 
        ### Promptize
        Returns a formatted version of `prompt`, which you can use to create
        your own `input` functions.

        #### ARGS:
        - `prompt`: the prompt message
        - `fgcolor`: the foreground color of prompt (default is `None` which uses no colors)
        - `bgcolor`: the background color of prompt (default is `None` which uses no colors)
        - `prompt_char`: the character(s) starting the prompt. (default is `None` which uses the default '>>')

        ```
        # Example
        >> pins.promptize('this is prompt')
        '>> this is prompt'
        >> pins.promptize('this is prompt', 'plum', prompt_char='$')
        '$ this is prompt'
        ```
        """
        prompt_char = prompt_char if prompt_char else self.PROMPT_CHAR
        s = f"{prompt_char} {prompt}"
        return self.colorize(s, fgcolor, bgcolor, attrs=attrs)

    @typecheck()
    def textalign_x(self, text: str, width: Optional[int] = None,
                    align: Union[XAlign, str] = "center", fill_char: str = " "):
        """
        ### Text Align X
        Align `text` on the x axis.

        #### ARGS:
        - `text`: the text string to align
        - `width`: the width that it should align within (`None` takes terminal's width)
        - `align`: the alignment position (default is `center`)
            (alignments: `center`, `left`, `right`)
        - `fill_char`: the character used for padding (default is `' '`)

        ```
        # Example
        >> pins.textalign_x("Align this", width=30)
        '          Align this          '
        >>
        >> pins.textalign_x("Align this", width=30, align="right")
        '                    Align this'
        ```

        Raises `AssertionError` if:
        - `align` is not left, center or right.
        """
        assert align in ("center", "left", "right"), f"Invalid align: '{
            align}'"

        if text == "":
            return text

        # Set the width to the terminal width, if None
        width = width if width else get_terminal_size()[0]

        newtext = []
        for line in text.splitlines():
            diff = len(line) - len(de_ansi(line))  # difference
            if align == "center":
                newtext.append(line.strip().center(width+diff, fill_char))
            elif align == "right":
                newtext.append(line.strip().rjust(width+diff, fill_char))
            else:
                newtext.append(line.strip().ljust(width+diff, fill_char))

        return "\n".join(newtext)

    @typecheck()
    def textalign_y(self, text: str, height: Optional[int] = None,
                    align: Union[YAlign, str] = "center", fill_char: str = " "):
        """
        ### Text Align Y
        Align `text` on the y axis.

        #### ARGS:
        - `text`: the text string to align
        - `height`: the height that it should align within (`None` takes terminal's height)
        - `align`: the alignment position (`top`, `center`, `bottom`)
        - `fill_char`: the character used for padding (default is `' '`)

        ```
        # Example
        >> pins.textalign_y("Align this.", height=1, align="center", fill_char=".")
        .
        Align this.
        .
        ```

        Raises `AssertionError` if:
        - `align` is not top, center or bottom.
        """
        assert align in ("center", "top", "bottom"), f"Invalid align: '{
            align}'"

        if not text:
            return text

        if height != None and height <= 0:
            return text

        height = height if height != None else (get_terminal_size()[1] // 2)
        pad = "\n".join([fill_char for _ in range(height)])
        padding_fmt = "%s\n%s\n%s"  # Format string

        if align == "top":
            return padding_fmt % (text, pad, pad)
        if align == "center":
            return padding_fmt % (pad, text, pad)
        if align == "bottom":
            return padding_fmt % (pad, pad, text)

    @typecheck()
    def indent_text(self, text: str, indent: int = 4, wrap: bool = True):
        """ 
        ### Indent Text
        Indents `text` to `indent` spaces (left to right)

        #### ARGS:
        - `text`: the text to indent
        - `indent`: number of characters to indent
        - `wrap`: wrap the text if exceeds terminal width

        ```
        # Example
        >> pins.indent_text("Indent this text to two spaces.", indent=2)
        '  Indent this text to two spaces.'
        >> 
        >> multiline_text = "This is a\\nmultiline text. it contains\\nnewline characters."
        >> pins.indent_text(multiline_text, indent=2)
          This is a
          multiline text. it contains
          newline characters.
        ```
        """
        max_width = get_terminal_size()[0]

        # Clip indent
        indent = min(indent, max_width-1)
        indent = max(indent, 0)

        # Wrap text if needed
        if wrap and max_width < (len(text)+indent):
            text = fill(text, max_width - indent)

        # Indent and Return
        pad = " "*indent
        return '\n'.join([pad+line for line in text.splitlines()])

    def for_each(self, items: Iterable[Any], func: Callable[[Any], Any]) -> list:
        """ 
        ### For Each
        As name implies, this method runs `func` for each item in `items`, 
        passing item to `func`.

        #### ARGS:
        - `items`: any iterable (e.g. `list`, `tuple`, `str` etc.)
        - `func`: function to call for each item (this function must accept an item)

        ```
        >> strings = ('paul', 'leto', 'jessica')
        >> pins.for_each(strings, str.title)
        ['Paul', 'Leto', 'Jessica']
        ```
        """
        return [func(item) for item in items]

    def wrap_text(self, text: str, width: int = None,
                  initial_indent: str = "",
                  subsequent_indent: str = "",
                  expand_tabs: bool = True,
                  tabsize: int = 8,
                  replace_whitespace: bool = True,
                  fix_sentence_endings: bool = False,
                  break_long_words: bool = True,
                  break_on_hyphens: bool = True,
                  drop_whitespace: bool = True,
                  max_lines: int = None,
                  placeholder: str = " [...]") -> str:
        """ 
        ### Wrap Text
        Wrap the text. This method is merely a thin wrapper around the `fill()`
        function from `textwrap` library.

        ```
        >> text = "Wrap this text if it exceeds 15 characters."
        >> pins.wrap_text(text, 15)
        Wrap this text
        if it exceeds
        15 characters.
        ```

        """
        # Terminal width if width None.
        width = width if width else get_terminal_size()[0]
        return fill(text=text,
                    width=width,
                    initial_indent=initial_indent,
                    subsequent_indent=subsequent_indent,
                    expand_tabs=expand_tabs,
                    tabsize=tabsize,
                    replace_whitespace=replace_whitespace,
                    fix_sentence_endings=fix_sentence_endings,
                    break_long_words=break_long_words,
                    break_on_hyphens=break_on_hyphens,
                    drop_whitespace=drop_whitespace,
                    max_lines=max_lines,
                    placeholder=placeholder)

    @typecheck()
    def splice_text(self, text: str, chars: str = "_", steps: int = 1) -> str:
        """ 
        ### Splice Text
        Inserts the `chars` AFTER each `i` characters within the text.

        #### ARGS
        - `text`: the text in which to insert the chars
        - `chars`: the characters to insert
        - `steps`: number of characters to jump before inserting

        ```
        # Example
        >> pins.splice_text("insert the characters")
        'i_n_s_e_r_t_ _t_h_e_ _c_h_a_r_a_c_t_e_r_s'
        >> pins.splice_text("insert the characters", "+", 2)
        'in+se+rt+ t+he+ c+ha+ra+ct+er+s'
        ```
        """
        steps = max(steps, 1)  # Ensure steps is positive

        if steps > len(text):
            return text

        # Is chars empty?
        if chars == '':
            return text

        return chars.join([text[i:i+steps] for i in range(0, len(text), steps)])

    def contains_ansi(self, text: str) -> bool:
        """ 
        ### Contains ansi
        Returns `True` if text contains ansi codes, else `False`.
        """
        return True if ANSI_REGEX.search(text) else False

    @typecheck()
    def shorten_path(self, p: str, n: int = 3, replacement: str = "...") -> str:
        """ 
        ### Shorten Path
        Truncate first `n` parts (exluding prefix) from `p` path. This method also
        never truncates the suffix (last part).

        #### ARGS:
        - `p`: the path to shorten
        - `n`: number of parts to truncate (`-1` to truncate maximum parts)
        - `replacement`: string placed in place of truncated parts

        ```
        >> path = "C:\\users\\username\\downloads"
        >> pins.shorten_path(path, 2)
        'C:\\...\\downloads'
        ```
        """
        if not p:
            return ""

        if n == 0 or n < -1:
            return p

        # Convert to Path object
        p: Path = Path(p)

        parts: list = list(p.parts)
        if len(parts) <= 2:
            return str(p)

        prefix = parts.pop(0)
        n = min(n, len(parts) - 1)  # Clip n at parts - 1

        return path_join(prefix, replacement, path_sep.join(parts[n:]))

    def now(self, format_: str = "%d %B %Y %I:%M %p") -> str:
        """  
        ### Now
        Returns the current local date & time, formatted as `format_`.
        This method is equivalent to `datetime.now().strftime(format_)`

        #### ARGS:
        - `format_`: the format of output datetime string 
            (default format returns as `25 September 2024 01:30 PM`)

        #### Format Codes:
        - `%d` day of the month as decimal (e.g. `01, 02, ... 31`)
        - `%j` day of the year as decimal (e.g. `001, 002, ... 366`)
        - `%a` Weekday as locale's abbr. name (e.g. `Sun, Mon, ... Sat`)
        - `%A` Weekday as locale's full name (e.g. `Sunday, Monday, ... Saturday`)
        - `%w` Weekday as decimal (starting from sunday) (e.g. `0, 1, ... 6`)
        - `%U` Week number of the year (Sunday as 1st day of week) (e.g. `00, 01, ... 53`)
        - `%W` Week number of the year (Monday as 1st day of week) (e.g. `00, 01, ... 53`)
        - `%b` Month as locale's abbr. name (e.g. `Jan, Feb, ... `Dec)
        - `%B` Month as locale's full name (e.g. `January, February, ... December`)
        - `%m` month as decimal (e.g. `01, 02, ... 12`)
        - `%Y` year with century (e.g. `2000, 2001, ... 9999`)
        - `%y` year without century (e.g. `00, 01, ... 99`)
        - `%p` Locale's equivalent of either AM or PM (e.g. `AM, PM`)
        - `%H` Hour (24-hour clock) (e.g. `00, 01, ... 23`)
        - `%I` Hour (12-hour clock) (e.g. `01, 02, ... 12`)
        - `%M` Minute (e.g. `00, 01, ... 59`)
        - `%S` Second (e.g. `00, 01, ... 59`)
        - `%f` Microsecond (6-digits) (e.g. `000000, 000001, ... 999999`)

        To learn more about format codes, see  `datetime` module in Python Docs.

        ```
        # Example
        >> pins.now(format_="%I:%M %p")
        '01:40 PM'
        >> pins.now(format_="%d %B %Y")
        '25 September 2024'
        >> pins.now(format_="%d %B %Y %I:%M %p")
        '25 September 2024 01:40 PM'
        ```
        """
        return datetime.now().strftime(format_)

    @typecheck()
    def format_date(self, date_string: str, format_: str) -> str:
        """ 
        ### Format Date
        Converts a date/time string to a human-readable format like `10 minutes ago` or 
        `6 years ago` etc. by subtracting the date/time from `date_string`
        from current date/time.

        #### ARGS:
        - `date_string`: string containing the datetime (e.g `25-09-2024 13:40:00`)
        - `format_`: the format of the `date_string` (e.g `%d-%m-%Y %H:%M:%S`)

        #### Format Codes:
        See Function Docstring of `Pins.now()`

        ```
        # Example
        >> datetime_string = "25-09-2024 14:02:00"
        >> pins.format_date(datetime_string, format_="%d-%m-%Y %H:%M:%S")
        '22 minutes ago'
        >>
        >> date_string = "25-09-2024"
        >> pins.format_date(date_string, format_="%d-%m-%Y")
        '14 hours ago'
        >>
        >> time_string = "14:02:00"
        >> pins.format_date(time_string, format_="%H:%M:%S")
        '22 minutes ago'
        >>
        >> time_string = pins.now("%H:%M:%S")
        >> time.sleep(3)
        >> pins.format_date(time_string, format_="%H:%M:%S")
        '3 seconds ago'
        ```
        """
        # Find Delta
        delta = datetime.now() - datetime.strptime(date_string, format_)

        # Convert to base units
        seconds = delta.seconds
        minutes = seconds // 60
        hours = minutes // 60

        days = delta.days
        months = days // 30
        years = months // 12
        centuries = years // 100

        # Format and return
        if centuries > 0:
            unit = "century" if centuries == 1 else "centuries"
            return f"{centuries} {unit} ago"
        if years > 0:
            unit = "year" if years == 1 else "years"
            return f"{years} {unit} ago"
        if months > 0:
            unit = "month" if months == 1 else "months"
            return f"{months} {unit} ago"
        if days > 0:
            unit = "day" if days == 1 else "days"
            return f"{days} {unit} ago"
        if hours > 0:
            unit = "hour" if hours == 1 else "hours"
            return f"{hours} {unit} ago"
        if minutes > 0:
            unit = "minute" if minutes == 1 else "minutes"
            return f"{minutes} {unit} ago"
        if seconds > 0:
            unit = "second" if seconds == 1 else "seconds"
            return f"{seconds} {unit} ago"
        else:
            return f"Just now"

    def get_calendar(self, year: int = None, month: int = None) -> str:
        """ 
        ### Get Calendar
        Returns a multi-column calendar of `month` of `year`. If both are `None`,
        Returns the calender of current month.

        #### ARGS:
        - `year`: the year of the calendar
        - `month`: the month of the year

        ```
        # Example
        >> pins.get_calendar()
           September 2024
        Mo Tu We Th Fr Sa Su
                           1
         2  3  4  5  6  7  8
         9 10 11 12 13 14 15
        16 17 18 19 20 21 22
        23 24 25 26 27 28 29
        30

        >> pins.get_calendar(2024, 9)
           September 2024
        Mo Tu We Th Fr Sa Su
                           1
         2  3  4  5  6  7  8
         9 10 11 12 13 14 15
        16 17 18 19 20 21 22
        23 24 25 26 27 28 29
        30

        >> pins.get_calendar(2024, None)
        --snip--
        ValueError: Either both year and month should be provided or none.
        ```

        Raises `AssertionError` if:
        - `month` is not in range `1-12`
        - one of `month` and `year` is None

        """
        # Get the current month (if not provided by user)
        if month == None and year == None:
            today = datetime.today()
            month, year = today.month, today.year

        if month == None or year == None:
            raise AssertionError(
                "Either both year and month should be provided or None.")

        assert month <= 12 and month > 0, f"Invalid month {
            month}: must be 1-12"

        return calendar_month(year, month)

    def print_calendar(self, year: int = None, month: int = None,
                       month_color: Color = None,
                       date_color: Color = None):
        """ 
        ### Print Calendar
        Prints calendar returned from `Pins.get_calendar(args)`.

        #### ARGS:
        - `year`: the year of the calendar
        - `month`: the month of the year
        - `month_color`: color of the first line (e.g `September 2024`)
        - `date_color`: color of the current date and day name (e.g `We` and `25`)

        Raises all exceptions raised by `Pins.get_calendar()`, `Pins.colorize()`
        and `Pins.colorize_regex()` methods upon invalid inputs.
        """

        calendar = self.get_calendar(year, month)
        if month_color == None and date_color == None:
            print(calendar)
            return

        calendar = calendar.splitlines()
        month_year = calendar[0]
        daynames = calendar[1]
        dates = '\n'.join(calendar[2:])

        day, dayname, year_, month_ = self.now("%d %a %Y %B").split()
        # Colorize the parts
        month_year_chunks = month_year.split()
        if month_year_chunks[0] == month_ and month_year_chunks[1] == year_:
            dates = self.colorize_regex(
                dates, r'\s%d\s' % int(day), date_color)
            daynames = self.colorize_regex(daynames, dayname[:-1], date_color)

        month_year = self.colorize(month_year, month_color)

        print('\n'.join([month_year, daynames, dates]))

    def create_ansi_fmt(self, fgcolor: Color = None, bgcolor: Color = None,
                        attrs: Iterable[Attribute] = None, color_mode: int = None) -> str:
        """
        ### Create Ansi Format
        Returns an ansi format string with a string placeholder and reset code.

        #### ARGS:
        - `fgcolor`: foreground color
        - `bgcolor`: background color
        - `attrs`: attributes list
        - `color_mode`: the color mode (uses module-level `COLOR_MODE` if color_mode `None`)

        This method sets `fgcolor` and `bgcolor` to `None` if the
        module-level `USE_COLORS` is set to False.

        #### Returns:
        `ANSI%sRESET` or `%s`

        ```
        # Example
        >> pins.create_ansi_fmt(fgcolor="light_red", color_mode=4)
        '\x1b[91m%s\x1b[0m'
        >>
        >> pins.create_ansi_fmt(fgcolor=None, color_mode=4)
        '%s'
        ```

        Raises all exceptions that `ansy.make_ansi()` would raise for invalid inputs.

        """
        color_mode = color_mode if color_mode else self.COLORMODE
        ansi_seq = self._make_ansi(fgcolor, bgcolor, attrs, color_mode)
        return f"{ansi_seq}%s{ANSI_CODES['reset']}" if ansi_seq else '%s'

    def _recurse_list(self, items: list,
                      level: int = 0,
                      list_indent: int = 4,
                      pad: str = "",
                      bullet: str = "+",
                      bullet_map: Iterable[Bullet] = None,
                      prefix_fmt: str = "%s",
                      item_fmt: str = "%s",
                      list_type: str = "unordered",
                      newline: str = "\n",
                      num_prefix: str = '') -> str:
        """ 
        Recursively traverse through items and create a list (the "str" list not the "list" list).
        Each list inside `items` will be indented.

        #### ARGS:
        - `items`: the items list
        - `list_indent`: the indentation of a level (a list in `items`)
        - `pad`: padding of the whole list
        - `bullet`: the bullet character(s) (ignored when `list_type` is `ordered`)
        - `bullet_map`: bullet characters for each level (ignored when `list_type` is `ordered`)
        - `prefix_fmt`: the formatting to apply to prefix
        - `item_fmt`: the formatting to apply to items
        - `list_type`: the type of list (`ordered` or `unordered`)
        - `newline`: the newline character(s)
        - `level`: level of list (Not to be touched by humans!)
        - `num_prefix`: prefix for numbered list (Not to be touched by humans!)


        Raises `TypeError` if:
        - `items` include anything except `str` and `list`
        """
        # Indentation in each level
        indent = (" "*list_indent)*level

        count = 1  # For numbered (ordered) list
        nest = [None]*len(items)  # Preallocation for current list
        for i, item in enumerate(items):
            # Choose prefix
            if list_type == "ordered":
                prefix = prefix_fmt % f"{num_prefix}{count}."
            else:
                if bullet_map:
                    bullet = bullet_map[min(level, len(bullet_map)-1)]
                prefix = prefix_fmt % bullet

            if isinstance(item, list):
                # IF list, recurse
                nest[i] = self._recurse_list(item, level+1, list_indent, pad,
                                             bullet, bullet_map, prefix_fmt,
                                             item_fmt, list_type, newline,
                                             f"{num_prefix}{i}.")
            elif isinstance(item, str):
                # IF str, add to nest
                nest[i] = f"{pad}{indent}{prefix} {item_fmt % item}"
                count += 1
            else:
                # IF other, Error
                raise TypeError(f"Unexpected type: {type(item)}")

        # Join the nest, create a string
        return newline.join(nest)

    def _render_menu(self, menu: list, selected_index: int, bullet: str = ">",
                     selected_ansi: str = None, normal_ansi: str = None):
        """
        Renders menu with ansi formatting
        #### ARGS:
        - `menu`: the menu list (a list of strings)
        - `selected_index`: the selected menu item
        - `bullet`: the bullet character(s)
        - `selected_ansi`: the ansi sequence for selected text
        - `normal_ansi`: the ansi sequence for normal text

        """
        normal_pad = len(de_ansi(bullet))
        for i, option in enumerate(menu):
            if i == selected_index:
                # Selected
                print(f"{bullet} {selected_ansi}{option}\033[0m", flush=True)
            else:
                # Normal
                print(f"{' '*normal_pad} {normal_ansi}{option}\033[0m",
                      flush=True)

    def _extract(self, text: str, pattern: Pattern):
        """ 
        ### Extract
        Extracts `pattern` from `text` and yields a match on each iteration.
        Returns a generator object.
        """
        for m in re.finditer(pattern, text):
            yield m.group(1)

    def _make_ansi(self, fgcolor: Color = None, bgcolor: Color = None,
                   attrs: Iterable[Attribute] = None, color_mode: int = None) -> str:
        """ 
        Interface between `ansy.make_ansi()` and `Pins`. It's just for `Pins`,
        you can safely use `ansy.make_ansi()` for you purposes.

        This method just sets `fgcolor` and `bgcolor` to `None` if the
        module-level `USE_COLORS` is set to False.
        """
        if not self.USE_COLORS:
            fgcolor, bgcolor = None, None

        return make_ansi(fgcolor, bgcolor, attrs, color_mode)

    def _assign_colors(self) -> dict:
        """ 
        Assign colors based on `COLOR_MODE`. Returns a dictionary.
        #### Keys in dictionary:
        `error` `info` `success` `warn`
        """
        match self.COLORMODE:
            case 4:
                # return 4-bit standard colors
                return {'info': "light_blue",
                        'success': "light_green",
                        'error': "light_red",
                        'warn': "light_yellow"}
            case 8:
                # Assign 8-bit 256 colors
                return {'info': "sky_blue_deep_6",
                        'success': "spring_green_3",
                        'error': "indian_red_2",
                        'warn': "orange_light_2"}

            case 24:
                # Assign 24-bit RGB colors (RGB TUPLES)
                return {'info': (79, 195, 247),
                        'success': (156, 204, 101),
                        'error': (255, 23, 68),
                        'warn': (255, 179, 0)}

            case _:
                raise ValueError("Invalid COLORMODE:", self.COLORMODE)

    def _validate_types(self, v: list[Tuple]):
        """ 
        ### Validate Types
        Validate the types of variable. Returns `True` if all vars are valid,
        Raises `TypeError` if any var not matched. It iterates through the `v` list
        and validates each tuple.

        #### Types supported:
        - `str`: check strings
        - `int`: check integers
        - `float`: check floating point numbers
        - `list`: check lists
        - `tuple`: check tuples
        - `set`: check sets
        - `dict`: check dictionaries
        - `bool`: check booleans
        - `None`: check nonetypes
        - `type`: check classes


        #### Syntax for v:
        - `[(str, var, type),(...),...,(...)]`
        - `('name of var', value of var, type(s) to match to)`

        ```
        >> # Example
        >> name = 'Anas'
        >> age = '22'
        >> pins.validate_type([('name', name, str),('age', age, int)])
        TypeError: 'age' must be int: not <class str>
        >>
        >> # Checking a var for multiple types
        >> number: str | None = 1
        >> pins.validate_type([('name', name, (str, None))])
        TypeError: 'age' must be str or None: not <class int>
        >>
        ```
        """
        for var in v:
            # If to check multiple types
            if isinstance(var[2], tuple):
                # Normalize var[2] for Nonetype
                expected_types = [type(t) if t == None else t for t in var[2]]

                if type(var[1]) in expected_types:
                    continue

                # If not matched with any type
                err = f"{var[0]} must be {' or '.join([str(t) for t in var[2]])}: not {
                    type(var[1])}"
                raise TypeError(err)

            else:
                # Check for single type
                expected_type = var[2] if var[2] != None else type(var[2])
                if type(var[1]) != expected_type:
                    err = f"{var[0]} must be {var[2]}: not {type(var[1])}"
                    raise TypeError(err)

        return True

    def _validate_colors(self, colors: list[Tuple]):
        """ 
        ### Validate Colors
        Validate the colors based on `COLORMODE`. Returns `True` if all colors are valid.
        Raises `InvalidColorError` if a color is invalid. It iterates through 
        the `colors` list and validates each tuple.

        #### Syntax for `colors`:
        - `[(str, var),(...),...,(...)]`
        - `('name of var', value of var)`

        ```
        >> # Example
        >> # Colormode is 24
        >> fg = 'orchid'
        >> bg = (255,15,16)
        >> bg_hex = '#344f5e'
        >> pins.validate_colors([('fg', fg),('bg', bg)])
        InvalidColorError: Invalid fg: 'orchid'
        >>
        ```
        """
        for name, clr in colors:
            if clr != None and not is_valid_color(clr, self.COLORMODE):
                err = f"Invalid {name}: {
                    clr}, maybe try a different color mode?"
                raise InvalidColorError(err)

        return True

    def _validate_attrs(self, attributes: list[Tuple]):
        """ 
        ### Validate Attrs
        Validate the attrs in `attributes`. Returns `True` if all attrs are valid.
        It iterates through the `attributes` list and validates each tuple.

        #### Syntax for `attributes`:
        - `[(str, list),(...),...,(...)]`
        - `('name of var', value of var (attrs list))`

        #### Example
        ```
        >> pins.validate_attrs([('attrs', attrs=['bold'])])
        True
        >> pins.validate_attrs([('attrs', attrs=None)])
        True
        >> pins.validate_attrs([('attrs', attrs=['bolf'])])
        AttributeError: Invalid attribute in attrs: 'bolf'
        >> pins.validate_attrs([('attrs', attrs=123)])
        AssertionError: attrs must be a list or tuple
        ```
        """
        for name, attrs in attributes:
            if attrs != None:
                assert isinstance(attrs, (list, tuple)), \
                    f"{name} must be a list or tuple"
                # Iterate through attrs
                for a in attrs:
                    if a not in ATTRIBUTES:
                        err = f"Invalid attribute in {name}: '{a}'"
                        raise AttributeError(err)

        return True

    def _longest_string(self, strings) -> str:
        """
        ### Longest String
        Traverses the Iterable (except strings) of strings and 
        returns the longest string in it.
        """
        assert isinstance(strings, Iterable), \
            "strings must be an iterable."

        return max(strings, key=len)


class Batched:
    """ 
    ### Batched
    Batch items of length `items_per_batch`. The last batch may be
    shorter than `items_per_batch`. Accepts any iterable that supports slicing `[:]`
    like `str`, `list`, `tuple` etc.

    Works similar to `batched()` from `itertools`, but also provides more
    information about the process like `total_batches`, `remaining_batches`, 
    `batch_no`, and `has_next_batch`. It also supports `with` statement.
    But unlike `batched()` which returns tuples, it returns the same type as input `items`.    

    #### ARGS:
    - `items`: an iterable that supports slicing (e.g `str`, `list`, `tuple`)
    - `items_per_batch`: number of items to yield per batch

    #### Example:
    ```
    >> my_string = "ABCDEFG"
    >> batches = Batched(my_string, 3)
    >> for batch in batches.iterate():
    ..     print(batch)
    ABC
    DEF
    G

    >> my_list = ['item 1', 'item 2', 'item 3', 'item 4', 'item 5']
    >> with Batched(my_list, 3) as batches:
    >>     for batch in batches.iterate():
    ..         print(batch)
    ['item 1', 'item 2', 'item 3']
    ['item 4', 'item 5']

    >> my_tuple = ('item 1', 'item 2', 'item 3', 'item 4', 'item 5')
    >> with Batched(my_list, 3) as batches:
    >>     for batch in batches.iterate():
    ..         print(f"Batch no: {batches.batch_no}", batch)
    ('item 1', 'item 2', 'item 3')
    ('item 4', 'item 5')
    ```
    """

    @typecheck()
    def __init__(self, items: Iterable[Any], items_per_batch: int = 4) -> None:
        self.items = items
        self.items_per_batch = items_per_batch
        self._total_items = len(self.items)

        self._calculate()

    def _calculate(self):
        self.batch_no = 1  # current page number
        self.total_batches = ceil(self._total_items/self.items_per_batch)
        self.remaining_batches = self.total_batches - 1
        self.has_next_batch: bool = True if self.total_batches > self.batch_no else False

    def iterate(self):
        """ yields a batch of length `items_per_page` from `items` on each iteration. """
        current_item = 0
        while current_item < self._total_items:
            if self.total_batches <= self.batch_no:
                self.has_next_batch = False

            stop_ = min(current_item + self.items_per_batch, self._total_items)
            yield self.items[current_item:stop_]

            current_item += self.items_per_batch
            self.batch_no += 1
            self.remaining_batches -= 1

        self._calculate()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class JsonHighlight:
    """ 
    ### JsonHighlight
    Pretty-print json with syntax highlighting.

    #### ARGS:
    - `indent`: number of spaces to indent
    - `quotes`: enable or disable quotations around keys and str values
    - `str_color`: color of string values
    - `number_color`: color of numeric values
    - `keyword_color`: color of keywords (`null`, `true`, `false` etc.)
    - `key_color`: color of object keys (`object` in json is `dict` in python)
    - `symbol_color`: color of symbols (`[,]{:}`)

    #### Example Usage:
    ```
    >> jsh = JsonHighlight()
    >> 
    >> with open('temp.json') as file:
    >>     new_json = jsh.highlight(json.load(file))
    >> print(new_json)
    {
        "name": "John",
        "age": 30,
        "details": {
            "is_admin": true
        }
    }
    ```
    """

    def __init__(self, indent: int = 4, quotes: bool = True,
                 color_mode: ColorMode = 4,
                 str_color: Color = "green",
                 number_color: Color = "yellow",
                 keyword_color: Color = "magenta",
                 key_color: Color = "red",
                 symbol_color: Color = "dark_grey",
                 other_color: Color = "cyan") -> None:

        self.indent = max(indent, 0)
        self.quotes = quotes
        self.color_mode = color_mode

        # Short for Format (format strings with %s placeholder)
        self.FMT = {
            "str": self._create_fmt(str_color, color_mode=self.color_mode),
            "number": self._create_fmt(number_color, color_mode=self.color_mode),
            "keyword": self._create_fmt(keyword_color, color_mode=self.color_mode),
            "key": self._create_fmt(key_color, color_mode=self.color_mode),
            "symbol": self._create_fmt(symbol_color, color_mode=self.color_mode),
            "other": self._create_fmt(other_color, color_mode=self.color_mode),
        }

        self.LEFT_BRACKET = self.FMT['symbol'] % "["
        self.RIGHT_BRACKET = self.FMT['symbol'] % "]"
        self.COMMA = self.FMT['symbol'] % ","
        self.LEFT_PAREN = self.FMT['symbol'] % "{"
        self.RIGHT_PAREN = self.FMT['symbol'] % "}"
        self.COLON = self.FMT['symbol'] % ":"

    def _create_fmt(self, fgcolor=None, bgcolor=None, attrs=None, color_mode=4):
        ansi_seq = make_ansi(fgcolor, bgcolor, attrs, color_mode)
        return f"{ansi_seq}%s{ANSI_CODES['reset']}" if ansi_seq else '%s'

    def _parse(self, data, level=0) -> str:
        """ Parse and colorize data """
        indent = " "*self.indent
        pad = indent * level
        quote_fmt = '"%s"' if self.quotes else "%s"

        if isinstance(data, dict):
            items = [None] * len(data)
            for i, (k, v) in enumerate(data.items()):
                value = self._parse(v, level + 1)
                items[i] = f"{pad}{indent}{self.FMT['key'] %
                                           (quote_fmt % k)}{self.COLON} {value}"

            paren_fmt = f"{self.LEFT_PAREN}\n%s\n{pad}{self.RIGHT_PAREN}"
            return paren_fmt % f"{self.COMMA}\n".join(items)

        elif isinstance(data, list):
            items = [self._parse(item, level + 1) for item in data]
            bracket_fmt = f"{self.LEFT_BRACKET}\n%s\n{pad}{self.RIGHT_BRACKET}"
            return bracket_fmt % f"{self.COMMA}\n".join(pad+indent+item for item in items)

        elif isinstance(data, str):
            return self.FMT['str'] % (quote_fmt % data)
        elif isinstance(data, bool):
            return self.FMT['keyword'] % str(data).lower()
        elif isinstance(data, (int, float)):
            return self.FMT['number'] % str(data)
        elif data is None:
            return self.FMT['keyword'] % "null"
        else:
            return self.FMT['other'] % str(data)

    @typecheck()
    def highlight(self, data: Any, indent: Optional[int] = None) -> str:
        """ 
        ### Highlight
        Applies Syntax Highlighting to Json `data`.

        #### ARGS:
        - `data`: json data as python object
        - `indent`: number of spaces to indent each level

        ```
        >> jsh = JsonHighlight()
        >> 
        >> with open('temp.json') as file:
        >>     new_json = jsh.highlight(json.load(file))
        >> print(new_json)
        {
            "name": "John",
            "age": 30,
            "details": {
                "is_admin": true
            }
        }
        ```
        """
        self.indent = indent if indent else self.indent
        return self._parse(data)


class Typewriter:
    """ 
    ### Typewriter
    Write text to `stdout` with a typewriter-like effect.

    #### ARGS:
    - `interval`: interval between each character print.

    #### Example:
    ```
    >> with Typewriter(interval=0.05) as writer:
    >>     writer.write("Write this text.")
    Write this text.
    ```
    """

    @typecheck()
    def __init__(self, interval: float = 0.025):
        assert interval >= 0, "interval must not be negative"
        self.interval = interval

    @typecheck()
    def write(self, value: Any, interval: Optional[float] = None, end: str = "\n"):
        """ 
        ### Write
        Write the `value` character by character to `stdout`.

        #### ARGS:
        - `value`: value to print. accepts any value (implicitly converts to `str`)
        - `interval`: interval between each character print (overrides module-level `interval`)
        - `end`: character to print after printing whole `value`.

        ```
        >> writer = Typewriter(0.01)
        >> writer.write("Write this text.")
        Write this text.

        >> with Typewriter(0.01) as writer:
        >>     writer.write("Write this text.")
        Write this text.
        ```

        Raises `AssertionError` if:
        - `interval` is less than 0
        """
        if interval:
            assert interval >= 0, "interval must not be negative"

        interval = interval if interval else self.interval
        try:
            for char in list(str(value)):
                sys.stdout.write(char)
                sys.stdout.flush()
                sleep(interval)
        except (KeyboardInterrupt, EOFError):
            pass
        sys.stdout.write(end)
        sys.stdout.flush()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class Box:
    """ 
    ### Box
    Create a frame (box) around text. 

    #### ARGS:
    - `text`: the text to create the box around
    - `width`: the width of the box (default is `None` which uses width of terminal)
        (only even numbers work, this method forces width to be even if it's odd)
    - `pad_x`: padding on X-axis within the box (number of characters)
    - `pad_y`: padding on Y-axis within the box (number of lines)
    - `x_align`: alignment of text on X-Axis (`left`, `center`, `right`)
    - `y_align`: alignment of text on Y-Axis (`top`, `center`, `bottom`)
    - `charset`: the charset to use (`ascii`, `blocks`, `box`, `box_double`, `box_heavy`, `box_round`)
    - `border_color`: color of the border
    - `text_color`: color of the text
    - `color_mode`: color_mode to use (`4`, `8`, `16`)

    #### Example:
    ```
    >> box = Box("A Box", 20, x_align="center")
    >> print(box.create())
    +------------------+
    |      A Box       |
    +------------------+
    >> print(box.create("Another Box"))
    +------------------+
    |   Another Box    |
    +------------------+
    ```
    Raises `ValueError` if:
    - `x_align` is invalid 
    - `y_align` is invalid 

    Raises `AssertionError` if:
    - `border_color` is invalid 
    - `text_color` is invalid 
    """

    @typecheck(skip=['border_color', 'text_color'])
    def __init__(self, text: Optional[str] = None,
                 width: Optional[int] = None,
                 pad_x: int = 0, pad_y: int = 0,
                 x_align: Union[XAlign, str] = "left",
                 y_align: Union[YAlign, str] = "top",
                 charset: Union[Charset, str, None] = None,
                 border_color: Color = None,
                 text_color: Color = None,
                 color_mode: int = 4) -> None:

        assert x_align in ("center", "left", "right"), f"Invalid x_align: '{
            x_align}'"
        assert y_align in {"center", "top",
                           "bottom"}, f"Invalid y_align: '{y_align}'"

        if border_color and not is_valid_color(border_color, color_mode):
            raise InvalidColorError(
                f"Invalid {color_mode}-bit color: '{border_color}'")
        if text_color and not is_valid_color(text_color, color_mode):
            raise InvalidColorError(
                f"Invalid {color_mode}-bit color: '{text_color}'")

        self.x_align = x_align
        self.y_align = y_align
        self.text = text
        self.width = width
        self.padding_x = pad_x
        self.padding_y = pad_y
        self.color_mode = color_mode

        try:
            self.charset: dict = CHARSETS[charset]
        except KeyError:
            # Fallback: ascii
            self.charset: dict = CHARSETS['ascii']

        self.border_color = border_color
        self.text_color = text_color

        self.border_fmt = make_ansi(border_color,
                                    color_mode=color_mode)+"%s"+ANSI_CODES['reset']
        self.text_fmt = make_ansi(text_color,
                                  color_mode=color_mode)+"%s"+ANSI_CODES['reset']

    def _calculate_width_padding(self, text, width, pad_x, pad_y, wrap):
        self.terminal_width = get_terminal_size()[0]
        self.width = max(width, 4) if width else self.terminal_width

        if not wrap:  # if wrap false, and width less than text
            self.width = max(self.width, len(text)+4)

        # Is width more than terminal width?
        self.width = min(self.width, self.terminal_width)

        # Is width odd?
        if self.width % 2 == 1:
            self.width -= 1  # reduce to make even
        self.width = max(self.width, 4)  # Clip width to 4 minimum

        # Paddings X, Y around text within box
        self.padding_x = max(pad_x, 0)  # Ensure pad_x is non-negative
        self.padding_y = max(pad_y, 0)

        # Is padding_x times 2 > half of width?
        half_width = (self.width / 2)
        if self.padding_x*2 >= half_width:
            self.padding_x = floor(half_width/2)

        # Force padding to be even
        if self.padding_x % 2 != 0:
            self.padding_x -= 1

    def _create_top_bottom_lines(self, fmt) -> tuple:
        """ Create top and bottom lines of the box """
        top_line = fmt % f"{self.charset['TOP_LEFT']}{
            self.charset['TOP_ST']*(self.width-2)}{self.charset['TOP_RIGHT']}"
        bottom_line = fmt % f"{self.charset['BOTTOM_LEFT']}{
            self.charset['BOTTOM_ST']*(self.width-2)}{self.charset['BOTTOM_RIGHT']}"

        return top_line, bottom_line

    def _create_mid_lines(self, text, width, x_align, charset, border_fmt, text_fmt):
        border_l = border_fmt % charset['LEFT_V']
        border_r = border_fmt % charset['RIGHT_V']

        mid_lines = ""
        for line in text.splitlines():
            lenline = len(de_ansi(line))
            empty_space = max((width - (self.padding_x * 2)) - lenline - 2, 0)
            rem_chars = max(width - (lenline + empty_space + 2), 0)

            # Is padding more than remaining chars?
            if self.padding_x >= rem_chars:
                self.padding_x = rem_chars // 2  # Set to half of rem_chars

            pad = " "*self.padding_x

            # Align line on x-axis
            line = self._align(line, len(line) + empty_space, align=x_align)

            mid_lines += f"{border_l}{pad}{text_fmt % line}{pad}{border_r}\n"

        return mid_lines

    def _align(self, text, width, align):
        newtext = []
        for line in text.splitlines():
            if align == "center":
                newtext.append(line.strip().center(width))
            elif align == "right":
                newtext.append(line.strip().rjust(width))
            else:
                newtext.append(line.strip().ljust(width))

        return "\n".join(newtext)

    def _create_padding_y(self, lines, width, charset, border_fmt):
        # Create padding Y
        padding_lines = ""
        for _ in range(lines):
            padding_lines += border_fmt % f"{charset['LEFT_V']}{
                " "*(width-2)}{charset['RIGHT_V']}" + '\n'

        return padding_lines.rstrip()

    def _ypad_midlines(self, mid_lines, padding, width,
                       charset, border_fmt, y_align):
        """ Add Y-Axis Padding to midlines """
        padding_y = self._create_padding_y(padding, width, charset, border_fmt)
        if not padding_y:
            return mid_lines

        if y_align == "top":
            return mid_lines + padding_y + "\n" + padding_y

        if y_align == "center":
            return padding_y + "\n" + mid_lines + padding_y

        if y_align == "bottom":
            return padding_y + "\n" + padding_y + "\n" + mid_lines

    @typecheck()
    def create(self, text: Optional[str] = None,
               width: Optional[int] = None,
               pad_x: Optional[int] = None,
               pad_y: Optional[int] = None,
               wrap: bool = False,
               replace_whitespace: bool = False) -> str:
        """
        ### Create 
        Create the box around `text`.

        #### ARGS:
        - `text`: the text to boxify (overrides the module-level `text`)
        - `width`: the width of box (overrides the module-level `width`)
        - `pad_x`: the padding on X-axis (overrides the module-level `pad_x`)
        - `pad_y`: the padding on Y-axis (overrides the module-level `pad_y`)
        - `wrap`: wrap the text
        - `replace_whitespace`: replace whitespaces with a single space.

        Raises `TypeError` if:
        - `text` is not a string or None.
        """
        text = text if text else self.text
        if text == "":
            return text

        width = width if width else self.width
        pad_x = pad_x if pad_x else self.padding_x
        pad_y = pad_y if pad_y else self.padding_y

        self._calculate_width_padding(text, width,
                                      pad_x, pad_y, wrap)

        # Wrap the text (if wrap true)
        if wrap and len(text) > self.width:
            text = fill(text, (self.width-2) - self.padding_x,
                        replace_whitespace=replace_whitespace)

        # Create top and bottom lines
        top_line, bottom_line = self._create_top_bottom_lines(self.border_fmt)

        # Create midlines
        mid_lines = self._create_mid_lines(text, self.width,
                                           self.x_align,
                                           self.charset,
                                           self.border_fmt,
                                           self.text_fmt)

        # ADD Y-Padding to the mid_lines
        mid_lines = self._ypad_midlines(mid_lines, self.padding_y, self.width,
                                        self.charset, self.border_fmt, self.y_align)

        # Join the lines and return
        return "\n".join([top_line, mid_lines.rstrip(), bottom_line])


class Validator:
    """ 
    ### Validator
    This class provides some validation methods. 

    #### NOTE:
    It is not a full-fledged validtor, for more advanced (proper) validations use 
    the `validators` (or similar) module.

    #### Validation methods:
    - `is_strong_password` Validation for strong passwords
    - `is_valid_extension` Validation for file extensions
    - `is_valid_filepath` Validation for filepaths
    - `is_valid_dirpath` Validation for directory paths
    - `is_valid_email` Validation for emails
    - `is_valid_url` Validation for urls
    - `is_valid_ip` Validation for ipaddresses (v4/v6)

    #### Example:
    ```
    >> Validator.is_email("someone@somewhere.com")
    True
    ```
    """
    OS: str = platform.system()

    def __init__(self) -> None:
        pass

    @classmethod
    def is_strong_password(cls, password: str) -> bool:
        """ 
        ### Is Strong Password
        Returns `True` if password is strong, `False` otherwise.

        #### Password Strength:
        A Password is strong if it satisfies following criteria:
        - it contains atleast one lowercase letter.
        - it contains atleast one uppercase letter.
        - it contains atleast one special character. ``'"~!@#$%^&*()_-+=`
        - it contains is atleast one digit.
        - it contains no whitespaces.
        - its length is atleast 8.

        #### Example
        ```
        # Contains an upper/lowercase letter, digit, special char, length >= 8
        >> is_strong_password("Passw0rd!")
        True
        # No uppercase letter, no special char
        >> is_strong_password("password123")
        False
        ```

        Raises `AssertionError` if:
        - `password` is not a string
        """
        assert isinstance(password, str), "password must be a string"
        if not password:
            return False

        if re.match(REGEX_PATTERNS['password'], password):
            return True
        return False

    @classmethod
    def is_valid_extension(cls, extension: str) -> bool:
        """
        ### Is Valid Extension
        Returns `True` if extension is valid, `False` otherwise.
        `extension` must contain a period `.`

        An extension is valid if it follows below criteria:
        - extension must be non-empty
        - extension must have a period `.`
        - extension must not contain symbols, whitespaces
            - `\\/:*?"<>|` are illegal on Windows
            - `/:` are illegal on Mac
            - `/` are illegal on Linux
        - extension must have atleast one character (excluding period)

        #### Example:
        ```
        >> pins.is_valid_extension(".txt")
        True
        >> pins.is_valid_extension(".py-c")
        True
        >> pins.is_valid_extension(".")
        False
        >> pins.is_valid_extension("txt")
        False
        ```

        Raises `AssertionError` if:
        - `extension` is not a string
        """
        assert isinstance(extension, str), \
            "extension must be a string."

        if not extension:
            return False

        if len(extension) < 2:
            return False

        if not extension.startswith("."):
            return False

        if extension.count(".") > 1:
            return False

        if " " in extension:
            return False

        if cls.OS == "Windows":
            for char in r'\/:*?"<>|':
                if char in extension:
                    return False
        elif cls.OS == "Darwin" and ('/' in extension or ':' in extension):
            return False
        elif cls.OS == "Linux" and '/' in extension:
            return False

        return True

    @classmethod
    def is_valid_filepath(cls, filepath: str, extension="*", max_length: int = 250) -> Literal[True] | str:
        """ 
        ### Is Valid Filepath
        Validates filepath. Returns `True` if valid, Returns `str` if invalid.
        This `str` contains the reason for path being invalid.

        #### ARGS:
        - `filepath`: the filepath string to validate
        - `extension`: the extension to match
            - `.py`: accept only .py files (any extension can be provided)
            - `*`: accept any extension
            - `None`: accept any extension (but not required!)
        - `max_length`: maximum length of the path (excluding extension, slashes and drive letter)

        #### Example:
        ```
        >> is_valid_filepath("path\\to\\fock.txt")
        True
        >> is_valid_filepath("path\\to\\f**k.txt")
        'Illegal characters are not allowed: \\/:?*<>|"'
        ```

        Raises `AssertionError` if:
        - `filepath` is not a string
        - `extension` is not a string or None
        - `extension` does not contain `*` or an extension (e.g `.py`)
        """
        assert isinstance(filepath, str), \
            "filepath must be a string."
        if extension != None:
            assert isinstance(extension, str), \
                "extension must be None or a string."

            assert extension.startswith(".") or extension == "*", \
                "extension must be set to '*' or an extension followed by a period."

        if not filepath:
            return "Path cannot be empty."

        # # Split filepath into root and extension
        root, ext_ = splitext(filepath)

        # # Root must not be empty
        if not root:
            return "Invalid filepath."

        dir_is_valid = cls.is_valid_dirpath(root, max_length)
        if dir_is_valid != True:
            return dir_is_valid

        # Extension Validation
        if isinstance(extension, str):
            if len(ext_) < 2:
                return "Filepath is missing an extension."
            if extension != '*' and ext_.lower() != extension.lower():
                return f"Only '{extension}' files are allowed."
            elif extension == '*' and not cls.is_valid_extension(ext_):
                return f"Invalid extension: '{ext_}'"
        else:
            if ext_ and not cls.is_valid_extension(ext_):
                return f"Invalid extension: '{ext_}'"

        return True

    @classmethod
    def is_valid_dirpath(cls, dirpath: str, max_length: int = 250):
        """ 
        ### Is Valid Dirpath
        Validates directory path. Returns `True` if valid, Returns `str` if invalid.
        This `str` contains the reason for path being invalid.

        #### ARGS:
        - `dirpath`: the path to validate
        - `max_length`: maximum length to allow (length of the whole path, except drive)

        #### Example:
        ```
        >> is_valid_dirpath("path\\to\\folder")
        True
        >> is_valid_dirpath("path\\to\\*Illegal*folder")
        'Illegal characters are not allowed: \\/:?*<>|"'
        ```

        Raises `AssertionError` if:
        - `dirpath` is not a string
        """
        assert isinstance(dirpath, str), \
            "dirpath must be a string."

        if not dirpath:
            return "Path must not be empty."

        d = Path(dirpath)
        if d.drive:
            root_parts = d.parts[1:]
        else:
            root_parts = d.parts

        if sum(len(part) for part in root_parts) > max_length:
            return f"Maximum length of path can be {max_length} (excluding slashes and drive)"

        # Check for illegal chars
        if cls.OS == "Windows":
            if cls._contains(root_parts, r'\/:?*<>"|'):
                return """Illegal characters are not allowed: '\\/:?*<>|"'"""
        elif cls.OS == "Darwin":
            if cls._contains(root_parts, r'/:?'):
                return """Illegal characters are not allowed: '/:?'"""
        else:
            if cls._contains(root_parts, r'/:?'):
                return "Illegal characters are not allowed: '/:?'"

        return True

    @classmethod
    def is_valid_email(cls, email: str) -> bool:
        """ 
        ### Is Valid Email
        Returns `True` if email is valid, `False` otherwise.

        #### Example:
        ```
        >> is_valid_email("simple@example.com")
        True
        >> is_valid_email("plainaddress")
        False
        ```

        Raises `AssertionError` if:
        - `email` is not a string
        """
        assert type(email) == str, "email must be a string."
        if re.match(REGEX_PATTERNS['email'], email):
            return True
        return False

    @classmethod
    def is_valid_url(cls, url: str) -> bool:
        """ 
        ### Is Valid URL
        Returns `True` if url is valid, `False` otherwise.

        #### Example:
        ```
        >> is_valid_url("https://example.com")
        True
        >> is_valid_url("www.example.com")
        False
        ```

        Raises `AssertionError` if:
        - `url` is not a string
        """
        assert type(url) == str, "url must be a string."
        if re.match(REGEX_PATTERNS['url'], url):
            return True
        return False

    @classmethod
    def is_valid_ip(cls, addr: str, version=4) -> bool:
        """ 
        ### Is Valid IP
        Returns `True` if ipaddress is valid, `False` otherwise.

        #### ARGS:
        - `addr`: the ipaddress to validate
        - `version`: the ipaddress version (`4` or `6`)

        #### Example:
        ```
        >> is_valid_ip("192.168.0.1", version=4)
        True
        >> is_valid_ip("2001:db8:85a3::8a2e:370:7334", version=6)
        True
        >> is_valid_ip("192.168.0.1", version=6)
        False
        ```

        Raises `AssertionError` if:
        - `addr` is not a string
        - `version` is not 4 or 6
        """
        assert type(addr) == str, "addr must be a string."
        assert version in (4, 6), f"Invalid version: {
            version}, must be 4 or 6."
        try:
            address = ipaddress.ip_address(addr)
        except ValueError:
            return False

        if address.version != version:
            return False

        return True

    @classmethod
    def _contains(cls, parts: Iterable[str], chars: str) -> bool:
        """
        ### Contains
        Checks whether a string in `parts` contains a character from `chars`. 
        Returns `True` if it does, `False` if does not.
        """
        for char in chars:
            for part in parts:
                if char in part:
                    return True
