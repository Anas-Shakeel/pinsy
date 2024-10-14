## Pins (*P*rints & *in*put*s*)

#### Outdated README: Almost everything is updated (changed) since i last wrote this readme.

A Helper Module For `Print` and `Input` related functions to speed up the
workflow of creating user-friendly command-line applications.

It consists of a number of input and print functions for specfic tasks like taking integers as input or printing an error message.

### Features

- Color support

- Fully customizable

- Easy to use

- blah, blah, blah, X, Y, Z... you know the drill.

### External Dependencies

There is only `1` external library used in this project.

- `colorama`: to fix windows terminal for color output (ancient terminals like powershell, cmd etc).

### Setup:

- Install [Python 3.9+](https://www.python.org/download) *(above `3.9`would be good, i have `version 3.12.2`)*
- Download and Extract this repository onto your machine.
- Open `terminal`  or `cmd` in the project's directory.
- Install dependencies by running `pip install -r requirements.txt`
- Done! now you can use the module in your scripts.

### Basic Usage:

Import this module into your application (script). I have created a script called `cli.py`

```python
# cli.py
from pins import Pins
```

Now create an instance of the `Pins` class.

```python
p = Pins()
```

Now you can use the input and print functions through the `p` object.

Let me show you a demo

```python
# cli.py
from pins import Pins
p = Pins()

# Taking int input
p.input_int() # This will ask user for an integer and will return that integer upon valid input.

# Taking str input
p.input_str() # This will take any input and will return the input as string.

# Printing error
p.print_error(error="This is an error.") # This will print the 'error' message
```

These functions have *optional* arguments which extend their functionality.

### Pins Class

This is the main *(and the only)* class of this module, which have to be instantiated before use. This class has a number of arguments that can be used to customize the module in a certain way.

```python
class pins.Pins(use_colors = False, full_colored_status = False,
           handle_errors = 'quit', error_callback = None, charset = 'ascii',
           prompt_char = '>>', menu_color = "dark_grey", prompt_color = "light_green",
           info_color = "light_blue", success_color = "light_magenta",
           error_color = "light_red", warn_color = "light_yellow")
```

These arguments may look overwhelming at first glance but they are really just some settings or options. Let's explore them one by one for you to better understand what each of them do and how to use them.

> #### Arguments:
> 
> `use_colors`: This `bool` decides whether to use colors in the output or not. (default is `False` which doesn't show any colors in the output in terminal)
> 
> 
> `full_colored_status`: This `bool` decides whether to use colors for the whole status string or just the special parts (status type string, bars, etc.). (default is `False` which uses colors only for special parts.)
> 
> `handle_errors`: This `str` decides how to handle errors like `KeyboardInterrupt` or `EOFError` which taking an input. (default is `quit` which simply quits the application using `sys.exit()`)
> 
> > `quit`: quits the application
> > 
> > `raise`: raises `KeyboardInterrupt` or `EOFError` for you to handle them yourself.
> > 
> > `callback`: calls the callback function provided in `error_callback` argmuent.
> 
> `error_callback`: This is the callback function that gets called when an error (`KeyboardInterrupt` or `EOFError`) occurs. only useful when `handle_errors` is set to `callback`.
> 
> `charset`: This `str` decides what characters to use in `boxify()` function to box the text (default is `ascii` which uses standard ascii characters). other charsets are `blocks`, `box`, `box_double`, `box_heavy`, `box_round`.
> 
> `prompt_char`: This `str` is the character(s) that is used in `input`s as prompt character (default is `>>`).
> 
> `menu_color`: This `str` is the name of the color used to print the menu. (default is `dark_grey`)
> 
> > These color names come from `termcolor` module which recognizes these color names. there are a number of color supported:
> > 
> > `white` `black` `grey` `red` `green` `yellow` `blue` `magenta` `cyan`
> > 
> > `light_grey` `light_red` `light_green` `light_yellow` `light_blue` `light_magenta` `light_cyan`
> > 
> > `dark_grey`
> > 
> > If provided an unrecognized color name, the default text color gets set for the menu *(same goes for other color arguments)*
> 
> `prompt_color`: This `str` is the name of the color used to print the prompt message in `input` functions. (default is `light_green`)
> 
> `info_color`: This `str` is the name of the color used to print the info message in the `print_info()` function. (default is `light_blue`)
> 
> `success_color`: This `str` is the name of the color used to print the success message in the `print_success()` function. (default is `light_magenta`)
> 
> `error_color`: This `str` is the name of the color used to print the error message in the `print_error()` function. (default is `light_red`)
> 
> `warn_color`: This `str` is the name of the color used to print the warning message in the `print_warning()` function. (default is `light_yellow`)



### Pins Methods

1. `input_int()`

> This method takes an integer input and returns the `int`. each `input` function asks user again and again upon invalid inputs until a valid input is entered or an error occurs. namely `KeyboardInterrupt` or `EOFError` which gets handeled according to `handle_errors` argument.
> 
> ##### Args:
> 
> - `prompt`: The message to print as prompt (defaults to `''` which uses the default prompt string)
> 
> - `min_`: minimum accepted integer (defaults to `None` which removes minimum constraint)
> 
> - `max_`: maximum accepted integer (defaults to `None` which removes maximum constraint)
> 
> ##### Usage:
> 
> ```python
> p = Pins()
> 
> # Taking an int input (negative or positive)
> p.input_int()
> 
> # Taking an int input (only values between 1 to 10 allowed)
> p.input_int(prompt="Enter a number between 1 & 10: ", min_=1, max_=10)
> ```
> 
> Raises `ValueError` if `min_` is greater than `max_`.

2. `input_float()`

> This method takes a float input and returns the `float`.
> 
> ##### Args:
> 
> - `prompt`: The message to print as prompt (defaults to `''` which uses the default prompt string)
> 
> - `min_`: minimum accepted float (defaults to `None` which removes minimum constraint)
> 
> - `max_`: maximum accepted float (defaults to `None` which removes maximum constraint)
> 
> ##### Usage:
> 
> ```python
> # Taking a float input (negative or positive)
> p.input_float()
> 
> # Taking an float input (only values between 0 to 1 allowed)
> p.input_float(prompt="Enter a float between 0 & 1: ", min_=0, max_=1)
> ```
> 
> Raises `ValueError` if `min_` is greater than `max_`.

3. `input_str()`

> This method takes a string input and returns the `str`.
> 
> ##### Args:
> 
> - `prompt`: The message to print as prompt (defaults to `''` which uses the default prompt string)
> 
> - `empty_allowed`: Whether to allow empty inputs (`True` allows empty inputs)
> 
> - `constraint`: Set a constraint to accept only a specific set of characters. constraints that can be used:
>   
>   - `only_alpha`: only alphabets allowed
>   
>   - `only_digits`: only digits allowed
>   
>   - `only_alnum`: only alphanumerics allowed
>   
>   (by default, `constraint` is set to `''` meaning every character is allowed.)
> 
> ##### Usage:
> 
> ```python
> # Taking a str input (any character)
> p.input_str()
> 
> # Taking a str input (non-empty, alphabets-only)
> p.input_str(prompt="Enter your name: ", empty_allowed=False, constraint="only_alpha")
> ```
> 
> Raises a `TypeError`, if `constraint` is not a `str` and `ValueError`, if set to an unrecognized string.

4. `input_yes_no()`

> This method takes a string input (`y` or `n` for yes and no) and returns the `bool`. `True` for `y` and `False` for `n`.
> 
> ##### Args:
> 
> - `prompt`: The message to print as prompt (defaults to `''` which uses the default prompt string)
> 
> ##### Usage:
> 
> ```python
> # Taking a yes or no input (y or n)
> p.input_yes_no()
> 
> # Taking a yes or no input (with custom prompt message)
> p.input_yes_no(prompt="Do you want to process? (y/n): ")
> ```

5. `input_email()`

> This method takes an `email` string as input and returns the `str`. **(Email is matched with a simplified version of a regex (regular expression) pattern that most browsers nowadays use to validate email addresses in the web forms)**.
> 
> ##### Args:
> 
> - `prompt`: The message to print as prompt (defaults to `''` which uses the default prompt string)
> 
> ##### Usage:
> 
> ```python
> # Taking email from user (any character)
> p.input_email()
> 
> # Taking email from user (with a custom prompt message)
> p.input_email(prompt="Enter your email address: ")
> ```

6. `input_password()`

> This method takes a `password` string as input and returns the `str`. This method hides the typed password characters to ensure privacy.
> 
> ##### Args:
> 
> - `prompt`: The message to print as prompt (defaults to `''` which uses the default prompt string)
> 
> - `constraint`: Set a constraint to accept only a specific set of characters. constraints that can be used:
>   
>   - `only_alpha`: only alphabets allowed
>   
>   - `only_digits`: only digits allowed
>   
>   - `only_alnum`: only alphanumerics allowed
>   
>   (by default, `constraint` is set to `''` meaning every character is allowed.)
> 
> ##### Usage:
> 
> ```python
> # Taking password from user (any character)
> p.input_password()
> 
> # Taking password from user (only digits allowed)
> p.input_password(prompt="Enter password (numerical only): ", constraint="only_digits")
> ```
> 
> Raises a `TypeError`, if `constraint` is not a `str` and `ValueError`, if set to an unrecognized string.



7. `input_file()`

> This method takes a filepath string as input and returns the `str`.
> 
> ##### Args:
> 
> - `prompt`: The message to print as prompt (defaults to `''` which uses the default prompt string)
> 
> - `ext`: Only accept a file with a specific extension. (`*` accepts every file)
>   
>   - `ext` must be provided with a `.` (e.g `.py` or `.txt` etc)
> 
> - `must_exist`: File must exist (defaults to `True`)
> 
> ##### Usage:
> 
> ```python
> # Taking path to a file (file doesn't need to exist)
> p.input_file()
> 
> # Taking path to a file (.py files that exist)
> p.input_file(prompt="Enter path a .py file: ", ext=".py", must_exist=True)
> ```
> 
> Raises `ValueError`, if `ext` is empty `''` or if `ext` does not start with a `.` (except `*`)

8. `input_dir()`

> This method takes a directory path string as input and returns the `str`.
> 
> ##### Args:
> 
> - `prompt`: The message to print as prompt (defaults to `''` which uses the default prompt string)
> 
> - `must_exist`: Directory must exist (defaults to `True`)
> 
> ##### Usage:
> 
> ```python
> # Taking path to a directory (directory doesn't need to exist)
> p.input_dir()
> 
> # Taking path to a directory (directory needs to exist)
> p.input_dir(prompt="Enter path to assets folder: ", must_exist=True)
> ```

9. `print_error()`

> This method prints the error message in a somewhat formatted way.
> 
> ##### Args:
> 
> - `error`: The error message to print. (raises `TypeError` if error not provided)
> 
> - `quit_too`: Whether to quit the application after printing the error (defaults to `False`)
> 
> ##### Usage:
> 
> ```python
> # Printing an error message
> p.print_error("This is an error message.")
> 
> # Printing an error message (Quits the application after printing)
> p.print_error("This is an error message.", quit_too=True)
> ```

10. `print_info()`

> This method prints the info message in a somewhat formatted way.
> 
> ##### Args:
> 
> - `info`: The info message to print. (raises `TypeError` if info not provided)
> 
> ##### Usage:
> 
> ```python
> # Printing an info message
> p.print_info("This is an info message.")
> ```

11. `print_warning()`

> This method prints the warning message in a somewhat formatted way.
> 
> ##### Args:
> 
> - `warning`: The warning message to print. (raises `TypeError` if warning not provided)
> 
> ##### Usage:
> 
> ```python
> # Printing an warning message
> p.print_warning("This is an warning message.")
> ```

12. `print_success()`

> This method prints the success message in a somewhat formatted way.
> 
> ##### Args:
> 
> - `success`: The success message to print. (raises `TypeError` if success not provided)
> 
> ##### Usage:
> 
> ```python
> # Printing an success message
> p.print_success("This is a success message.")
> ```

13. `print_menu()`

> This method prints a menu in a somewhat formatted way.
> 
> ##### Args:
> 
> - `menu`: list of the menu item strings.
> - `heading`: heading of the menu (leave empty `''` for no heading)
> 
> ##### Usage:
> 
> ```python
> # Printing a menu (without heading)
> menu = ["Login", "Signup", "Quit"]
> p.print_menu(menu)
> 
> # Printing a menu (with heading)
> p.print_menu(menu, heading="Main Menu")
> ```

14. `boxify()`

> This method Returns a formatted version of `heading` in a box. __(although by default, it uses the 'character-set' set by `charset` argument of the `Pins` class, you can change the charset by given a recognized `charset` at function call)__.
> 
> ##### Args:
> 
> - `text`: Text string to wrap in a box.
> 
> - `width`: Width of the box _(number of characters wide)_
>    (default is `None` which takes up the available width in the terminal)
>
> - `charset`: Charset to use
>
> - `border_color`: Color of the border of the box
>
> - `text_color`: Color of the text within the box
> 
> - `bold`: Boolean `True` or `False` which Bolds the text _(may not work on some terminals)_
> 
> - `underline`: Boolean `True` or `False` which Underlines the text
> 
> ##### Errors:
> This method raises below exceptions on some situations.
> 
> ###### Raises `TypeError` if:
> - `text` is not `str`
> 
> ###### Raises `ValueError` if:
> - `border_color` is unrecognized
> - `text_color` is unrecognized
> 
> 
> ##### Usage:
> 
> ```python
> # Boxifying a text string
> p.boxify("This text will be wrapped in a box")
> 
> 
> # Boxifying a text string (with other options)
> text = "This text will be wrapped in a box"
> p.boxify(s, charset="blocks", border_color="magenta", bold=True, underline=True)
> ```



---

Author : `Anas Shakeel`
Source Code:  `https://www.github.com/Anas-Shakeel/Pins-module`
