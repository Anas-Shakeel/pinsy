"""
### Tests for Pinsy 
These are all the tests for pinsy module. 

#### How to run?
```
# Some functions rely on the terminal width/height (pytest conflicts)
>> python ./test_pinsy.py
```

#### pinsy.Pins()
- `test_boxify`
- `test_colorize_4bit`
- `test_colorize_8bit`
- `test_colorize_24bit`
- `test_colorize_regex`
- `test_contains_ansi`
- `test_create_ansi_fmt`
- `test_create_hr`
- `test_create_list_ordered`
- `test_create_list_unordered`
- `test_create_status`
- `test_create_table`
- `test_for_each`
- `test_format_date`
- `test_get_calendar`
- `test_indent_text`
- `test_now`
- `test_promptize`
- `test_shorten_path`
- `test_splice_text`
- `test_textalign_x`
- `test_textalign_y`
- `test__longest_string`
- `test__validate_types`
- `test__validate_colors`
- `test__validate_attrs`

#### pinsy.Validator()
- `test_is_strong_password`
- `test_is_valid_extension`
- `test_is_valid_filepath`
- `test_is_valid_dirpath`
- `test_is_valid_ip`
- `test_is_valid_url`
- `test_is_valid_email`

#### pinsy.utils
- `test_type_match`
- `test_type_check`

"""

from pinsy import Pins, Validator
from pinsy.utils import typecheck, type_match
from ansy import printc, colored, exceptions, ATTRIBUTES
from pytest import raises
import re
from datetime import datetime


CURRENT_OS = Validator.OS

pins = Pins()

# DONT CHANGE THESE DUMMIES PLEASE!!! Used by tests.
dummy = "This is a dummy string."
dummy_lg = "pine ordinary factor control bear use nation after blind loss deep serve stiff give railroad cry whale gone save sing wire bank ear swamThis is a dummy string."
dummy_items = ['item 1', 'item 2', 'item 3', 'item 4', 'item 5']
dummy_dict = {
    "name": "Pinsy",
    "author": "Anas Shakeel",
    "repository": "https://github.com/Anas-Shakeel/pinsy",
    "created": None
}


# pinsy.Pins Tests

def test_pins():
    p = Pins()

    # Colormodes
    p.set_colormode(4)
    p.set_colormode(8)
    p.set_colormode(24)
    with raises(AssertionError):
        p.set_colormode(250)
    with raises(AssertionError):
        p.set_colormode("invalid colormode")

    # Promptchars
    assert p.promptize("prompt: ") == '>> prompt: '
    assert p.promptize("Your name: ", prompt_char=">") == '> Your name: '
    assert p.promptize("Your name: ", prompt_char=123) == '123 Your name: '

    # Charsets
    assert p.create_hr(5) == '-----'
    p.set_charset("box")
    assert p.create_hr(5) == '─────'
    p.set_charset("blocks")
    assert p.create_hr(5) == '■■■■■'

    with raises(AssertionError):
        p.set_charset("invalid charset")
    with raises(AssertionError):
        p.set_charset(123)

    with raises(AssertionError):
        Pins(handle_errors=123)
    with raises(ValueError):
        Pins(handle_errors="something")

    # Renew Pins instance
    p = Pins()
    assert p.colorize("testing", "red") == '\x1b[31mtesting\x1b[0m'

    p.disable_colors()
    assert p.colorize("testing", "red") == 'testing'
    p.enable_colors()


def test_colorize_4bit():
    # Test 4-bit
    assert pins.colorize(dummy) == "This is a dummy string."
    assert pins.colorize(dummy, fgcolor="red", bgcolor="dark_grey", attrs=(
        'bold', 'italic')) == "\x1b[3m\x1b[1m\x1b[100m\x1b[31mThis is a dummy string.\x1b[0m"
    assert pins.colorize(123, fgcolor="red", bgcolor="dark_grey", attrs=[
                         'bold', 'italic']) == "\x1b[3m\x1b[1m\x1b[100m\x1b[31m123\x1b[0m"
    assert pins.colorize("", fgcolor="red", attrs=['bold', 'italic']) == ""
    assert pins.colorize(None, bgcolor="dark_grey",
                         attrs=['bold', 'italic']) == ""

    with raises(exceptions.ColorModeError):
        pins.colorize(dummy, "light_red", color_mode="4")

    with raises(AttributeError):
        pins.colorize(dummy, "light_red", attrs=['bol'])

    with raises(AssertionError):
        pins.colorize(dummy, "light_red", attrs="bol")

    with raises(AssertionError):
        pins.colorize(dummy, "light_red", attrs=123)

    with raises(exceptions.InvalidColorError):
        pins.colorize(dummy, "light_r")


def test_colorize_8bit():
    # Test 8-bit
    assert pins.colorize(dummy, color_mode=8) == "This is a dummy string."

    assert pins.colorize(dummy, fgcolor="plum", bgcolor="sea_green", attrs=[
                         'bold', 'italic'], color_mode=8) == "\x1b[3m\x1b[1m\x1b[48;5;78m\x1b[38;5;183mThis is a dummy string.\x1b[0m"
    assert pins.colorize(123, fgcolor="plum", bgcolor="sea_green", attrs=[
                         'bold', 'italic'], color_mode=8) == "\x1b[3m\x1b[1m\x1b[48;5;78m\x1b[38;5;183m123\x1b[0m"

    assert pins.colorize(dummy, fgcolor=250, bgcolor=20, attrs=[
                         'bold', 'italic'], color_mode=8) == "\x1b[3m\x1b[1m\x1b[48;5;20m\x1b[38;5;250mThis is a dummy string.\x1b[0m"
    assert pins.colorize(123, fgcolor="plum", bgcolor=25, attrs=[
                         'bold', 'italic'], color_mode=8) == "\x1b[3m\x1b[1m\x1b[48;5;25m\x1b[38;5;183m123\x1b[0m"

    assert pins.colorize("", fgcolor="brown_sandy", attrs=[
                         'bold', 'italic'], color_mode=8) == ""
    assert pins.colorize(None, bgcolor="dark_grey", attrs=[
                         'bold', 'italic'], color_mode=8) == ""

    with raises(exceptions.InvalidColorError):
        pins.colorize(dummy, "#555", color_mode=8)

    with raises(exceptions.InvalidColorError):
        pins.colorize(dummy, "light_reds", color_mode=8)

    with raises(exceptions.InvalidColorError):
        pins.colorize(dummy, 258, color_mode=8)


def test_colorize_24bit():
    # Test 24-bit
    assert pins.colorize(dummy, color_mode=24) == "This is a dummy string."

    assert pins.colorize(dummy, fgcolor=(255, 52, 52), bgcolor=(50, 50, 50), attrs=[
                         'bold', 'italic'], color_mode=24) == "\x1b[3m\x1b[1m\x1b[48;2;50;50;50m\x1b[38;2;255;52;52mThis is a dummy string.\x1b[0m"
    assert pins.colorize(123, fgcolor=(255, 52, 52), bgcolor=(50, 50, 50), attrs=[
                         'bold', 'italic'], color_mode=24) == "\x1b[3m\x1b[1m\x1b[48;2;50;50;50m\x1b[38;2;255;52;52m123\x1b[0m"

    assert pins.colorize(dummy, fgcolor="fff", bgcolor="#555555", attrs=[
                         'bold', 'italic'], color_mode=24) == "\x1b[3m\x1b[1m\x1b[48;2;85;85;85m\x1b[38;2;255;255;255mThis is a dummy string.\x1b[0m"
    assert pins.colorize(123, fgcolor=(255, 255, 255), bgcolor="#555555", attrs=[
                         'bold', 'italic'], color_mode=24) == "\x1b[3m\x1b[1m\x1b[48;2;85;85;85m\x1b[38;2;255;255;255m123\x1b[0m"

    assert pins.colorize("", fgcolor="#356456", attrs=[
                         'bold', 'italic'], color_mode=24) == ""
    assert pins.colorize(None, bgcolor="#524658", attrs=[
                         'bold', 'italic'], color_mode=24) == ""

    with raises(exceptions.InvalidColorError):
        pins.colorize(dummy, "red", color_mode=24)

    with raises(exceptions.InvalidColorError):
        pins.colorize(dummy, "plum", color_mode=24)

    with raises(exceptions.InvalidColorError):
        pins.colorize(dummy, (256, 258, 256), color_mode=24)


def test_colorize_regex():
    assert pins.colorize_regex("", "", "red") == ""
    assert pins.colorize_regex(dummy, "") == "This is a dummy string."
    assert pins.colorize_regex("8008135 is a number", re.compile(r"[0-9]+"),
                               fgcolor="red") == '\x1b[31m8008135\x1b[0m is a number'

    assert pins.colorize_regex(dummy, pattern="This", fgcolor="yellow", bgcolor="dark_grey", attrs=[
                               'strike']) == "\x1b[9m\x1b[100m\x1b[33mThis\x1b[0m is a dummy string."
    assert pins.colorize_regex(dummy, pattern="s",
                               fgcolor="yellow") == "Thi\x1b[33ms\x1b[0m i\x1b[33ms\x1b[0m a dummy \x1b[33ms\x1b[0mtring."

    assert pins.colorize_regex(dummy, pattern=re.compile(r"[ast]"),
                               fgcolor="yellow") == "Thi\x1b[33ms\x1b[0m i\x1b[33ms\x1b[0m \x1b[33ma\x1b[0m dummy \x1b[33ms\x1b[0m\x1b[33mt\x1b[0mring."
    assert pins.colorize_regex(dummy, re.compile(
        r"\s"), bgcolor="light_red") == 'This\x1b[101m \x1b[0mis\x1b[101m \x1b[0ma\x1b[101m \x1b[0mdummy\x1b[101m \x1b[0mstring.'

    with raises(TypeError):
        pins.colorize_regex("None", None)

    with raises(AssertionError):
        pins.colorize_regex(None, "s", "yellow")

    with raises(AssertionError):
        pins.colorize_regex(123, "s", "yellow")

    with raises(AssertionError):
        pins.colorize_regex(dummy, "This", attrs="bol")
    with raises(AssertionError):
        pins.colorize_regex(dummy, "This", attrs=1234)
    with raises(AttributeError):
        pins.colorize_regex(dummy, "This", attrs=["bold", "underfine"])

    with raises(exceptions.InvalidColorError):
        pins.colorize_regex(dummy, "This", "yellows")

    with raises(exceptions.InvalidColorError):
        pins.colorize_regex(dummy, "This", "plum")


def test_create_hr():
    pins.create_hr(None)  # Should run successfully
    pins.create_hr(2, charset=None)  # Should run successfully

    assert len(pins.create_hr(10)) == 10
    assert len(pins.create_hr(90)) == 90
    assert len(pins.create_hr(10, align="left")) == 10
    assert pins.create_hr(10, fill_char="-") == "----------"
    assert pins.create_hr(10, pad_x=2) == "--------"

    with raises(AssertionError):  # Invalid width
        pins.create_hr(0)  # must be greater than 0

    with raises(AssertionError):
        pins.create_hr(-500)

    with raises(TypeError):  # Invalid fillchar
        pins.create_hr(10, fill_char=1)

    with raises(AssertionError):  # Invalid charset
        pins.create_hr(10, charset="invalidcharset")

    with raises(AssertionError):  # Invalid align
        pins.create_hr(10, align="something")

    with raises(exceptions.InvalidColorError):  # Invalid Color
        pins.create_hr(10, color="redish")


def test_create_status():
    label = "test"

    assert pins.create_status("", "") == ""
    assert pins.create_status("asd", "") == ""
    assert pins.create_status(
        label, dummy) == "█ test: This is a dummy string."
    assert pins.create_status(label, dummy, "light_blue", "dark_grey", ['bold'],
                              "light_green", "dark_grey", ['italic']) == "\x1b[1m\x1b[100m\x1b[94m█ test: \x1b[0m\x1b[3m\x1b[100m\x1b[92mThis is a dummy string.\x1b[0m"

    # Label and text
    with raises(AssertionError):
        pins.create_status(123, 1.25)
    with raises(AssertionError):
        pins.create_status(None, None)

    # Colors
    with raises(exceptions.InvalidColorError):
        pins.create_status(label, dummy, label_fg="asdf")
    with raises(exceptions.InvalidColorError):
        pins.create_status(label, dummy, label_fg="red", text_fg="redish")

    # Attrs
    with raises(AttributeError):
        pins.create_status(label, dummy, text_attrs=['vold'])
    with raises(AssertionError):
        pins.create_status(label, dummy, text_attrs=123)
    with raises(AssertionError):
        pins.create_status(label, dummy, text_attrs="bold")


def test_boxify():
    assert pins.boxify("", 5) == ""
    assert pins.boxify(
        dummy, 30) == "+----------------------------+\x1b[0m\n|\x1b[0mThis is a dummy string.     \x1b[0m|\x1b[0m\n+----------------------------+\x1b[0m"
    assert pins.boxify(dummy, 30, x_align="center", y_align="center", border_color="blue",
                       text_color="green") == "\x1b[34m+----------------------------+\x1b[0m\n\x1b[34m|\x1b[0m\x1b[32m  This is a dummy string.   \x1b[0m\x1b[34m|\x1b[0m\n\x1b[34m+----------------------------+\x1b[0m"
    assert pins.boxify(
        dummy, 6, wrap=True) == "+----+\x1b[0m\n|\x1b[0mThis\x1b[0m|\x1b[0m\n|\x1b[0mis a\x1b[0m|\x1b[0m\n|\x1b[0mdumm\x1b[0m|\x1b[0m\n|\x1b[0my st\x1b[0m|\x1b[0m\n|\x1b[0mring\x1b[0m|\x1b[0m\n|\x1b[0m.   \x1b[0m|\x1b[0m\n+----+\x1b[0m"
    assert pins.boxify(dummy, 30, wrap=True, pad_x=2,
                       x_align="center") == "+----------------------------+\x1b[0m\n|\x1b[0m  This is a dummy string. \x1b[0m  |\x1b[0m\n+----------------------------+\x1b[0m"

    with raises(TypeError):
        pins.boxify(123456)
    with raises(TypeError):
        pins.boxify(None)

    with raises(TypeError):
        pins.boxify(dummy, "123")

    with raises(AssertionError):
        pins.boxify(dummy, x_align="Center")
    with raises(AssertionError):
        pins.boxify(dummy, y_align="Center")

    with raises(exceptions.InvalidColorError):
        pins.boxify(dummy, border_color="cyanish")
    with raises(exceptions.InvalidColorError):
        pins.boxify(dummy, border_color=404)

    with raises(exceptions.InvalidColorError):
        pins.boxify(dummy, text_color="cyanish")
    with raises(exceptions.InvalidColorError):
        pins.boxify(dummy, text_color=404)


def test_create_list_ordered():
    assert pins.create_list_ordered([]) == None
    assert pins.create_list_ordered(dummy_items, num_color="magenta", num_attrs=['bold'], item_color="green", item_attrs=[
                                    'italic']) == '\x1b[1m\x1b[35m1.\x1b[0m \x1b[3m\x1b[32mitem 1\x1b[0m\n\x1b[1m\x1b[35m2.\x1b[0m \x1b[3m\x1b[32mitem 2\x1b[0m\n\x1b[1m\x1b[35m3.\x1b[0m \x1b[3m\x1b[32mitem 3\x1b[0m\n\x1b[1m\x1b[35m4.\x1b[0m \x1b[3m\x1b[32mitem 4\x1b[0m\n\x1b[1m\x1b[35m5.\x1b[0m \x1b[3m\x1b[32mitem 5\x1b[0m'
    assert pins.create_list_ordered(
        dummy_items) == '1. item 1\n2. item 2\n3. item 3\n4. item 4\n5. item 5'
    assert pins.create_list_ordered(
        tuple(dummy_items)) == '1. item 1\n2. item 2\n3. item 3\n4. item 4\n5. item 5'
    assert pins.create_list_ordered(
        dummy_items, line_height=1) == "1. item 1\n\n2. item 2\n\n3. item 3\n\n4. item 4\n\n5. item 5"
    assert pins.create_list_ordered(dummy_items, indent=4, list_indent=2, num_color="magenta",
                                    item_color="green") == '    \x1b[35m1.\x1b[0m \x1b[32mitem 1\x1b[0m\n    \x1b[35m2.\x1b[0m \x1b[32mitem 2\x1b[0m\n    \x1b[35m3.\x1b[0m \x1b[32mitem 3\x1b[0m\n    \x1b[35m4.\x1b[0m \x1b[32mitem 4\x1b[0m\n    \x1b[35m5.\x1b[0m \x1b[32mitem 5\x1b[0m'
    assert pins.create_list_ordered(["Starting multi-level list", dummy_items, "Ending multi-level list",], num_color="magenta", num_attrs=['bold'], item_color="green", item_attrs=[
                                    'italic']) == '\x1b[1m\x1b[35m1.\x1b[0m \x1b[3m\x1b[32mStarting multi-level list\x1b[0m\n    \x1b[1m\x1b[35m1.1.\x1b[0m \x1b[3m\x1b[32mitem 1\x1b[0m\n    \x1b[1m\x1b[35m1.2.\x1b[0m \x1b[3m\x1b[32mitem 2\x1b[0m\n    \x1b[1m\x1b[35m1.3.\x1b[0m \x1b[3m\x1b[32mitem 3\x1b[0m\n    \x1b[1m\x1b[35m1.4.\x1b[0m \x1b[3m\x1b[32mitem 4\x1b[0m\n    \x1b[1m\x1b[35m1.5.\x1b[0m \x1b[3m\x1b[32mitem 5\x1b[0m\n\x1b[1m\x1b[35m2.\x1b[0m \x1b[3m\x1b[32mEnding multi-level list\x1b[0m'

    with raises(TypeError):
        pins.create_list_ordered("dummy_items")
    with raises(TypeError):
        pins.create_list_ordered(dummy_items, indent="123")
    with raises(TypeError):
        pins.create_list_ordered(dummy_items, list_indent="123")
    with raises(TypeError):
        pins.create_list_ordered(dummy_items, line_height="123")

    with raises(exceptions.InvalidColorError):
        pins.create_list_ordered(
            dummy_items, num_color="magentas", num_attrs=['bold'])
    with raises(AttributeError):
        pins.create_list_ordered(
            dummy_items, num_color="magenta", num_attrs=['bolds'])


def test_create_list_unordered():
    assert pins.create_list_unordered([]) == None
    assert pins.create_list_unordered(["Starting multi-level list", dummy_items, "Ending multi-level list",],
                                      bullet_map=['+', '-'], bullet_color="magenta", bullet_attrs=['bold'],
                                      item_color="green", item_attrs=['italic']) == '\x1b[1m\x1b[35m+\x1b[0m \x1b[3m\x1b[32mStarting multi-level list\x1b[0m\n    \x1b[1m\x1b[35m-\x1b[0m \x1b[3m\x1b[32mitem 1\x1b[0m\n    \x1b[1m\x1b[35m-\x1b[0m \x1b[3m\x1b[32mitem 2\x1b[0m\n    \x1b[1m\x1b[35m-\x1b[0m \x1b[3m\x1b[32mitem 3\x1b[0m\n    \x1b[1m\x1b[35m-\x1b[0m \x1b[3m\x1b[32mitem 4\x1b[0m\n    \x1b[1m\x1b[35m-\x1b[0m \x1b[3m\x1b[32mitem 5\x1b[0m\n\x1b[1m\x1b[35m+\x1b[0m \x1b[3m\x1b[32mEnding multi-level list\x1b[0m'
    assert pins.create_list_unordered(dummy_items, "+", indent=4, list_indent=2, line_height=1,
                                      bullet_color="magenta", bullet_attrs=['bold'],
                                      item_color="green", item_attrs=['italic', 'underline']) == '    \x1b[1m\x1b[35m+\x1b[0m \x1b[4m\x1b[3m\x1b[32mitem 1\x1b[0m\n\n    \x1b[1m\x1b[35m+\x1b[0m \x1b[4m\x1b[3m\x1b[32mitem 2\x1b[0m\n\n    \x1b[1m\x1b[35m+\x1b[0m \x1b[4m\x1b[3m\x1b[32mitem 3\x1b[0m\n\n    \x1b[1m\x1b[35m+\x1b[0m \x1b[4m\x1b[3m\x1b[32mitem 4\x1b[0m\n\n    \x1b[1m\x1b[35m+\x1b[0m \x1b[4m\x1b[3m\x1b[32mitem 5\x1b[0m'
    assert pins.create_list_unordered(["Starting multi-level list", dummy_items, "Ending multi-level list",],
                                      bullet_map="+-") == '+ Starting multi-level list\n    - item 1\n    - item 2\n    - item 3\n    - item 4\n    - item 5\n+ Ending multi-level list'

    with raises(TypeError):
        pins.create_list_unordered("dummy_items")
    with raises(TypeError):
        pins.create_list_unordered(dummy_items, bullet=123)
    with raises(TypeError):
        pins.create_list_unordered(dummy_items, bullet_map=123)
    with raises(TypeError):
        pins.create_list_unordered(dummy_items, indent="123")
    with raises(TypeError):
        pins.create_list_unordered(dummy_items, list_indent="123")
    with raises(TypeError):
        pins.create_list_unordered(dummy_items, line_height="123")

    with raises(exceptions.InvalidColorError):
        pins.create_list_unordered(dummy_items, bullet_color="magentas",
                                   bullet_attrs=['bold'])
    with raises(AttributeError):
        pins.create_list_unordered(dummy_items, bullet_color="magenta",
                                   bullet_attrs=['bolds'])


def test_create_table():
    assert pins.create_table({}, values_fg="green") == None
    assert pins.create_table(dummy_dict, values_fg="green",
                             ignore_none=False) == 'name           \x1b[32mPinsy\x1b[0m\nauthor         \x1b[32mAnas Shakeel\x1b[0m\nrepository     \x1b[32mhttps://github.com/Anas-Shakeel/pinsy\x1b[0m\ncreated        \x1b[32mNone\x1b[0m'
    assert pins.create_table(dummy_dict, heading="About Pinsy", line_height=0,
                             heading_fg="magenta", heading_attrs=['reverse'],
                             keys_fg="dark_grey", values_fg="green") == '\x1b[7m\x1b[35mAbout Pinsy\x1b[0m\n \n\x1b[90mname      \x1b[0m     \x1b[32mPinsy\x1b[0m\n\x1b[90mauthor    \x1b[0m     \x1b[32mAnas Shakeel\x1b[0m\n\x1b[90mrepository\x1b[0m     \x1b[32mhttps://github.com/Anas-Shakeel/pinsy\x1b[0m'

    with raises(TypeError):
        pins.create_table("Dummy Dummy")

    with raises(TypeError):
        pins.create_table(dummy_dict, line_height="123")

    with raises(TypeError):
        pins.create_table(dummy_dict, indent_values="123")


def test_promptize():
    assert pins.promptize(123) == ">> 123"
    assert pins.promptize(None, prompt_char="PROMPT") == "PROMPT None"
    assert pins.promptize(dummy) == ">> This is a dummy string."
    assert pins.promptize(
        dummy, "red") == '\x1b[31m>> This is a dummy string.\x1b[0m'
    assert pins.promptize(dummy, "green", "dark_grey", ['bold'],
                          prompt_char=">") == '\x1b[1m\x1b[100m\x1b[32m> This is a dummy string.\x1b[0m'

    with raises(exceptions.InvalidColorError):
        pins.promptize(None, fgcolor="li")
    with raises(exceptions.InvalidColorError):
        pins.promptize(None, bgcolor="li")
    with raises(exceptions.InvalidColorError):
        pins.promptize(None, fgcolor="red", bgcolor="li")
    with raises(AttributeError):
        pins.promptize(None, attrs=["li"])
    with raises(AttributeError):
        pins.promptize(None, attrs=["bold", 123])


def test_textalign_x():
    assert pins.textalign_x("", 50) == ""
    assert pins.textalign_x(dummy,
                            50) == '             This is a dummy string.              '
    assert pins.textalign_x(dummy, 50, align="right",
                            fill_char="+") == '+++++++++++++++++++++++++++This is a dummy string.'

    with raises(AssertionError):
        pins.textalign_x(dummy, align="righty")
    with raises(TypeError):
        pins.textalign_x(1234)
    with raises(TypeError):
        pins.textalign_x(dummy, align=123)
    with raises(TypeError):
        pins.textalign_x(dummy, width="123")
    with raises(TypeError):
        pins.textalign_x(dummy, fill_char=123)


def test_textalign_y():
    assert pins.textalign_y("", 5) == ""
    assert pins.textalign_y(dummy, 0) == dummy
    assert pins.textalign_y(dummy, -100) == dummy
    assert pins.textalign_y(
        dummy, 3) == ' \n \n \nThis is a dummy string.\n \n \n '
    assert pins.textalign_y(
        dummy, 3, align="top") == 'This is a dummy string.\n \n \n \n \n \n '
    assert pins.textalign_y(
        dummy, 3, align="bottom") == ' \n \n \n \n \n \nThis is a dummy string.'
    assert pins.textalign_y(
        dummy, 3, fill_char="..") == "..\n..\n..\nThis is a dummy string.\n..\n..\n.."

    with raises(AssertionError):
        pins.textalign_y(dummy, align="topsy")
    with raises(TypeError):
        pins.textalign_y(1234)
    with raises(TypeError):
        pins.textalign_y(dummy, align=123)
    with raises(TypeError):
        pins.textalign_y(dummy, height="123")
    with raises(TypeError):
        pins.textalign_y(dummy, fill_char=123)


def test_indent_text():
    assert pins.indent_text("") == ''
    assert pins.indent_text(dummy) == '    This is a dummy string.'
    assert pins.indent_text(
        dummy, 50, True) == '                                                  This is a dummy string.'

    with raises(TypeError):
        pins.indent_text(123)
    with raises(TypeError):
        pins.indent_text(dummy, "5")


def test_splice_text():
    assert pins.splice_text(dummy, "+", 4) == "This+ is +a du+mmy +stri+ng."
    assert pins.splice_text(dummy, "(+)", 1) == "(+)".join(dummy)
    assert pins.splice_text(dummy, "(+)", -50) == "(+)".join(dummy)
    assert pins.splice_text(dummy, "(+)", 0) == "(+)".join(dummy)

    with raises(TypeError):
        pins.splice_text(None)
    with raises(TypeError):
        pins.splice_text(1234, "+", 4)
    with raises(TypeError):
        pins.splice_text(dummy, "+", "123")
    with raises(TypeError):
        pins.splice_text(dummy, 1, 5)


def test_contains_ansi():
    assert not pins.contains_ansi(pins.colorize(""))
    assert not pins.contains_ansi(pins.colorize(dummy))

    assert pins.contains_ansi(pins.colorize(
        dummy, "red", "dark_grey", ['bold', 'underline']))
    assert pins.contains_ansi(pins.colorize(
        dummy, "brown_sandy", "dark_grey", ['bold', 'underline'], 8))
    assert pins.contains_ansi(pins.colorize(
        dummy, "#B00B1E", "#C0DDE5", ['bold', 'underline'], 24))

    with raises(TypeError):
        pins.contains_ansi(123)
    with raises(TypeError):
        pins.contains_ansi(None)


def test_shorten_path():
    absolute_path = "C:\\users\\downloads\\files\\music\\song.mp3"
    relative_path = ".\\downloads\\files\\music\\song.mp3"
    relative_path_2 = "downloads\\files\\music\\song.mp3"

    assert pins.shorten_path(absolute_path, 0) == absolute_path
    assert pins.shorten_path(absolute_path, -1) == "C:\\...\\song.mp3"
    assert pins.shorten_path(absolute_path, 8000) == "C:\\...\\song.mp3"
    assert pins.shorten_path(
        absolute_path, n=1) == "C:\\...\\downloads\\files\\music\\song.mp3"

    assert pins.shorten_path(relative_path, n=0) == relative_path
    assert pins.shorten_path(relative_path, n=-1) == "downloads\\...\\song.mp3"
    assert pins.shorten_path(
        relative_path, n=800) == "downloads\\...\\song.mp3"
    assert pins.shorten_path(
        relative_path, n=1) == "downloads\\...\\music\\song.mp3"

    assert pins.shorten_path(relative_path_2, n=0) == relative_path_2
    assert pins.shorten_path(
        relative_path_2, n=-1) == "downloads\\...\\song.mp3"
    assert pins.shorten_path(
        relative_path_2, n=800) == "downloads\\...\\song.mp3"
    assert pins.shorten_path(
        relative_path_2, n=1) == "downloads\\...\\music\\song.mp3"

    assert pins.shorten_path("") == ""
    assert pins.shorten_path("somefolder") == "somefolder"
    assert pins.shorten_path("somefile.txt") == "somefile.txt"

    assert pins.shorten_path(
        absolute_path, n=3, replacement="") == "C:\\music\\song.mp3"
    assert pins.shorten_path(
        absolute_path, n=3, replacement="123") == "C:\\123\\music\\song.mp3"

    with raises(TypeError):
        pins.shorten_path(123)
    with raises(TypeError):
        pins.shorten_path(None)
    with raises(TypeError):
        pins.shorten_path("somefile.txt", n="1")
    with raises(TypeError):
        pins.shorten_path("somefile.txt", replacement=123)


def test_now():
    dt_format = "%d %B %Y %I:%M %p"
    dt_datetime = datetime.now().strftime(dt_format)
    dt_pins = pins.now(dt_format)

    assert dt_datetime == dt_pins
    assert pins.now("asd") == "asd"
    assert pins.now("") == ""

    with raises(TypeError):
        pins.now(123)
    with raises(TypeError):
        pins.now(None)


def test_for_each():
    items = ["Paul", "leto", "jessica"]

    assert pins.for_each(items, str.title) == ["Paul", "Leto", "Jessica"]
    assert pins.for_each(items, str.upper) == ["PAUL", "LETO", "JESSICA"]
    assert pins.for_each(items, str.lower) == ["paul", "leto", "jessica"]
    assert pins.for_each(items, len) == [4, 4, 7]
    assert pins.for_each([], str.lower) == []

    with raises(TypeError):
        pins.for_each(None, str.lower)
    with raises(TypeError):
        pins.for_each(items, None)
    with raises(TypeError):
        pins.for_each(items, "string")
    with raises(TypeError):
        pins.for_each(items, 1234)


def test_format_date():
    from time import sleep

    dt_format = "%I:%M:%S %p"

    time = pins.now(dt_format)
    sleep(1)
    assert pins.format_date(time, dt_format) == "1 second ago"
    assert pins.format_date(pins.now(dt_format), dt_format) == "Just now"

    with raises(TypeError):
        pins.format_date(None, None)
    with raises(TypeError):
        pins.format_date(None, 'None')
    with raises(TypeError):
        pins.format_date('None', None)
    with raises(TypeError):
        pins.format_date(123, "123")
    with raises(TypeError):
        pins.format_date("", 123)


def test_get_calendar():
    today = datetime.now()

    assert today.strftime("%B %Y") in pins.get_calendar()
    assert str(today.year) in pins.get_calendar()
    assert "May 2024" in pins.get_calendar(2024, 5)
    assert "January 1999" in pins.get_calendar(1999, 1)

    with raises(AssertionError):
        pins.get_calendar(0, 0)
    with raises(AssertionError):
        pins.get_calendar(2024, 13)
    with raises(AssertionError):
        pins.get_calendar(2024, None)
    with raises(AssertionError):
        pins.get_calendar(None, 5)


def test_create_ansi_fmt():
    assert pins.create_ansi_fmt() == "%s"

    fmt_4bit = pins.create_ansi_fmt("red", "dark_grey", ['bold', 'underline'])
    assert fmt_4bit == colored("%s", "red", "dark_grey", ['bold', 'underline'])

    fmt_8bit = pins.create_ansi_fmt(
        "plum", "brown_sandy", ['bold'], color_mode=8)
    assert fmt_8bit == colored("%s", "plum", "brown_sandy", [
                               'bold'], color_mode=8)

    fmt_24bit = pins.create_ansi_fmt(
        "#FFF", (255, 200, 200), ['bold'], color_mode=24)
    assert fmt_24bit == colored("%s", "#FFF", (255, 200, 200), [
                                'bold'], color_mode=24)

    with raises(exceptions.InvalidColorError):
        pins.create_ansi_fmt("")
    with raises(exceptions.InvalidColorError):
        pins.create_ansi_fmt("red", "")
    with raises(AttributeError):
        pins.create_ansi_fmt("red", "blue", "bold")
    with raises(AttributeError):
        pins.create_ansi_fmt("red", "blue", ["bols"])

    with raises(exceptions.ColorModeError):
        pins.create_ansi_fmt("red", color_mode=2)
    with raises(exceptions.ColorModeError):
        pins.create_ansi_fmt("red", color_mode="4")


def test__validate_types():
    valid_data = [
        ("None", None, None),
        ("int", 25, int),
        ("float", 2.5, float),
        ("str", "25", str),
        ("bool", False, bool),
        ("list", [25, 2.5, 2, 5], list),
        ("tuple", (25, 2.5, 2, 5), tuple),
        ("dict", {"name": "pinsy", "version": 1.0}, dict),
    ]
    assert pins._validate_types(valid_data)

    with raises(TypeError):
        pins._validate_types([("int", 2.5, int)])
    with raises(TypeError):
        pins._validate_types([("float", 25, float)])
    with raises(TypeError):
        pins._validate_types([("str", True, str)])


def test__validate_colors():
    default_colormode = pins.COLORMODE

    pins.set_colormode(4)
    colors_4 = [
        ("fg", 'red'),
        ("bg", 'blue'),
    ]
    assert pins._validate_colors(colors_4)

    with raises(exceptions.InvalidColorError):
        pins._validate_colors([("color", "plum")])  # 8-bit color
    with raises(exceptions.InvalidColorError):
        pins._validate_colors([("color", 8)])  # 8-bit color

    pins.set_colormode(8)
    colors_8 = [
        ("fg", 'orchid'),
        ("bg", 250),
    ]
    assert pins._validate_colors(colors_8)

    with raises(exceptions.InvalidColorError):
        pins._validate_colors([("color", "#B00B1E")])  # 24-bit color
    with raises(exceptions.InvalidColorError):
        pins._validate_colors([("color", (255, 25, 2))])  # 24-bit color

    pins.set_colormode(24)
    colors_24 = [
        ("fg", '#B00B1E'),
        ("bg", (255, 15, 16)),
    ]
    assert pins._validate_colors(colors_24)

    with raises(exceptions.InvalidColorError):
        pins._validate_colors([("color", "red")])  # 4-bit color
    with raises(exceptions.InvalidColorError):
        pins._validate_colors([("color", "brown_sandy")])  # 8-bit color
    with raises(exceptions.InvalidColorError):
        pins._validate_colors([("color", 250)])  # 8-bit color

    pins.set_colormode(default_colormode)


def test__validate_attrs():
    assert pins._validate_attrs([("attrs", list(ATTRIBUTES.keys()))])
    assert pins._validate_attrs([("attrs", None)])

    # Invalid attr type
    with raises(AssertionError):
        pins._validate_attrs([("attr1", 123)])
    with raises(AssertionError):
        pins._validate_attrs([("attr1", "string")])

    # Invalid attr
    with raises(AttributeError):
        pins._validate_attrs([("attr1", ['bolf', 'underfine'])])
    with raises(AttributeError):
        pins._validate_attrs([("attr2", ['strife', 'conceafed'])])


def test__longest_string():
    strings = [
        "Carolyn Newman"
        "subject",
        "cutting waste business",
        "women begun balance lay crop",
        "future fresh dot poetry care inch move married",
    ]

    assert pins._longest_string(strings) == strings[-1]
    assert pins._longest_string(ATTRIBUTES.keys()) == max(ATTRIBUTES.keys(),
                                                          key=len)

    with raises(TypeError):
        pins._longest_string([123, 321, 132, 231])

    with raises(AssertionError):
        pins._longest_string(123)


# pinsy.Validator Test


def test_is_strong_password():
    valid_passwords = [
        "Passw0rd!",
        "A1b2C3@4",
        "P@ssw0rd12",
        "MyStr0ng#Pwd",
        "Test123$",
    ]
    for pwd in valid_passwords:
        assert Validator.is_strong_password(pwd)

    invalid_passwords = [
        "",  # Empty
        "password123",  # No uppercase, no special
        "PASSWORD123!",  # no lowercase
        "Passw0rd",  # no special
        "P@ssword",  # no digit
        "Pass 123!",  # contains a space
        "Sh0rt!",  # too short, less than 8
    ]

    for pwd in invalid_passwords:
        assert Validator.is_strong_password(pwd) == False

    with raises(AssertionError):
        Validator.is_strong_password(None)
    with raises(AssertionError):
        Validator.is_strong_password(123)


def test_is_valid_extension():
    valid_exts = [".py", ".java", ".c", ".c++", ".txt",
                  ".py-c", ".py_c", ".MD", ".somethinglonger"]

    for ext in valid_exts:
        assert Validator.is_valid_extension(ext)

    if CURRENT_OS == "Windows":
        invalid_exts = ["", ".", ".c**", ".Ja va", '."py"',
                        ".py|c", "..MD", ".C::", ".p/y"]
        for ext in invalid_exts:
            assert Validator.is_valid_extension(ext) == False
        assert Validator.is_valid_extension(".tx\\t") == False
    elif CURRENT_OS == "Darwin":
        assert Validator.is_valid_extension(".tx\\t")
        assert Validator.is_valid_extension(".tx/t") == False
    else:  # Linux
        assert Validator.is_valid_extension(".tx\\t")
        assert Validator.is_valid_extension(".tx/t") == False


def test_is_valid_filepath():
    if CURRENT_OS == "Windows":
        valid_paths_win = [
            "file.txt",  # Normal
            "Documents\\file.txt",  # Normal relative
            "C:\\Users\\Username\\Documents\\file.txt",  # Normal Absolute
            "C:\\Users\\Username\\Documents\\Longpath\\very\\long\\path\\to\\a\\deeply\\nested\\file.txt",  # long path
            "C:\\Program Files\\app.exe",  # Contains space
            "D:\\Documents\\file.txt",  # Different drive
            "\\\\NetworkShare\\SharedFolder\\file.docx",  # Network path (UNC)
            "C:\\Windows\\System32\\drivers\\etc\\hosts",  # System filepath
            "C:\\Users\\Username\\Documents\\Documents\\",  # trailing backslash
            # Forward slashes (valid in windows)
            "C:/Users/Username/Documents/file.txt",
            "C:\\Users\\Username\\file/with\\mixed\\slashes.txt",  # Mixed slashes
            "C:\\Users\\Username\\Documents\\file",  # missing extension, but valid
            "C:\\Users\\Username\\Desktop\\UnicodeÆÓÇ│▓█▌▌τì←∞?♫¢chars.txt",  # Unicode chars
        ]
        for fpath in valid_paths_win:
            assert Validator.is_valid_filepath(fpath, extension=None)

        # Invalid filepath , ILLEGAL CHARS <>
        assert isinstance(Validator.is_valid_filepath("C:\\Users\\Username\\Desktop\\Invalid<file>.txt",
                                                      extension=None), str)

    else:  # Mac/Linux
        valid_paths = [
            "file.txt",  # just file
            "/home/username/Documents/file.txt",  # Normal fullpath
            "/usr/local/bin/executable",  # Path to bin
            "/home/username/Desktop/Valid<file>.txt",  # <> chars
            "/home/username/Projects/My Project/file.txt",  # Contains space
            "/var/log/syslog",  # Sysmtem log file
            "/home/username/Documents/folder/.hiddenfile",  # Hidden file
            "/home/username/Documents/folder/",  # Trailing slash
            "/mnt/data/file with unicode ÆÓÇ│▓█▌▌τì←∞?♫¢.txt",  # Unicode chars
            "/home//username//file.txt",  # Double slashes
            "/home/username/Documents/Longpath/very/long/path/to/a/deeply/nested/file.txt",  # Long path
            "~/Documents/file.txt",  # tilde as home dir shorthand
            "/home/username/symlink_to_file",  # symlink path
        ]
        for fpath in valid_paths:
            assert Validator.is_valid_filepath(fpath, extension=None)

    # Other Tests
    assert Validator.is_valid_filepath("file", extension=None)
    assert Validator.is_valid_filepath("file.py", extension=None)
    assert Validator.is_valid_filepath("file.c", extension="*")
    assert Validator.is_valid_filepath("file.java", extension="*")
    assert Validator.is_valid_filepath("file.cpp", extension=".cpp")

    assert isinstance(Validator.is_valid_filepath(
        "file.txt", extension=".py"), str)
    assert isinstance(Validator.is_valid_filepath(
        "file", extension=".py"), str)
    assert isinstance(Validator.is_valid_filepath("file", extension="*"), str)
    assert isinstance(Validator.is_valid_filepath(
        "path\\to\\a\\deeply\\nested\\file.txt", max_length=10), str)
    assert isinstance(Validator.is_valid_filepath(
        "path\\to\\a\\deeply\\nested\\file.txt", max_length=100), bool)
    assert isinstance(Validator.is_valid_filepath("file.<txt>"), str)
    assert isinstance(Validator.is_valid_filepath("file.tx t"), str)
    assert isinstance(Validator.is_valid_filepath(
        "file.tx t", extension=None), str)
    assert isinstance(Validator.is_valid_filepath(
        "file.*txt*", extension=None), str)

    with raises(AssertionError):
        Validator.is_valid_filepath(123)
    with raises(AssertionError):
        Validator.is_valid_filepath("file.txt", extension=123)
    with raises(AssertionError):
        Validator.is_valid_filepath("file.txt", extension="123")
    with raises(AssertionError):
        Validator.is_valid_filepath("file.txt", extension="txt")


def test_is_valid_dirpath():
    if CURRENT_OS == "Windows":
        valid_paths_win = [
            "folder",  # Normal
            "folder.txt",  # Folde with period (as file extensions)
            "Documents\\folder",  # Normal relative
            "C:\\Users\\Username\\Documents\\folder",  # Normal Absolute
            "C:\\Users\\Username\\Documents\\Longpath\\very\\long\\path\\to\\a\\deeply\\nested\\folder",  # long path
            "C:\\Program Files\\app data\\assets",  # Contains spaces
            "D:\\Documents\\folder",  # Different drive
            "\\\\NetworkShare\\SharedFolder\\folder",  # Network path (UNC)
            "C:\\Windows\\System32\\drivers\\etc\\hosts",  # System
            "C:\\Users\\Username\\Documents\\Documents\\",  # trailing backslash
            # Forward slashes (valid in windows)
            "C:/Users/Username/Documents/folder",
            "C:\\Users\\Username\\path/with\\mixed\\slashes",  # Mixed slashes
            "C:\\Users\\Username\\Desktop\\UnicodeÆÓÇ│▓█▌▌τì←∞?♫¢chars",  # Unicode chars
        ]
        for fpath in valid_paths_win:
            assert Validator.is_valid_dirpath(fpath)

        # ILLEGAL CHARS <>
        assert isinstance(Validator.is_valid_dirpath(
            "C:\\Invalid<file>.txt"), str)

    else:  # Mac/Linux
        valid_paths = [
            "folder",  # just file
            "/home/username/Documents/folder",  # Normal fullpath
            "/usr/local/bin/",  # Path to bin
            "/home/username/Desktop/Valid<folder>",  # <> chars
            "/home/username/My Project/folder 1",  # Contains space
            "/home/username/Documents/folder/",  # Trailing slash
            "/mnt/data/folder with unicode ÆÓÇ│▓█▌▌τì←∞?♫¢",  # Unicode chars
            "/home//username//folder",  # Double slashes
            "/home/username/Documents/Longpath/very/long/path/to/a/deeply/nested/folder",  # Long path
            "~/Documents/folder",  # tilde as home dir shorthand
        ]
        for fpath in valid_paths:
            assert Validator.is_valid_filepath(fpath, extension=None)

    # Other Tests
    assert isinstance(Validator.is_valid_dirpath(
        "path\\to\\a\\deeply\\nested\\folder", max_length=10), str)  # Length
    assert isinstance(Validator.is_valid_dirpath(""), str)  # Empty not allowed
    assert isinstance(Validator.is_valid_dirpath(
        "folder 0 | folder 1"), str)  # illegal chars
    assert isinstance(Validator.is_valid_dirpath(
        "folder.<txt>"), str)  # illegal chars

    with raises(AssertionError):
        Validator.is_valid_dirpath(123)


def test_is_valid_ip():
    valid_ip_v4 = [
        "192.168.0.1",
        "0.0.0.0",
        "255.255.255.255",
        "127.0.0.1",
        "1.1.1.1",
        "8.8.8.8",
        "172.16.254.1",
    ]
    invalid_ip_v4 = [
        "256.256.256.256",
        "192.168.1",
        "192.168.1.1.1",
        "192.168.-1.1",
        "192.168.1.01",
        "1234.56.78.90",
    ]
    for ip in valid_ip_v4:
        assert Validator.is_valid_ip(ip, version=4)
    for ip in invalid_ip_v4:
        assert Validator.is_valid_ip(ip, version=4) == False

    valid_ip_v6 = [
        "::1",
        "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
        "2001:db8:85a3::8a2e:370:7334",
        "::ffff:192.168.0.1",
        "fe80::1",
        "2001:0:3238:DFE1:63::FEFB",
    ]
    invalid_ip_v6 = [
        "12345::",
        "2001:::1",
        "2001:db8:85a3::8a2e:3707334",
        ":",
    ]
    for ip in valid_ip_v6:
        assert Validator.is_valid_ip(ip, version=6)
    for ip in invalid_ip_v6:
        assert Validator.is_valid_ip(ip, version=6) == False

    with raises(AssertionError):
        Validator.is_valid_ip(192)
    with raises(AssertionError):
        Validator.is_valid_ip("192.168.0.1", version="4")
    with raises(AssertionError):
        Validator.is_valid_ip("192.168.0.1", version=2)


def test_is_valid_url():
    valid_urls = [
        "http://example.com",
        "https://example.com",
        "ftp://example.com",
        "http://www.example.com",
        "https://www.example.com",
        "http://blog.example.com",
        "https://shop.example.co.uk",
        "http://sub.domain.example.com",
        "http://example.com/path",
        "https://example.com/path/to/resource",
        "http://example.com/path/to/resource/",
        "http://example.com/path?name=value",
        "https://example.com/path/to/resource?name=value&other=another",
        "http://example.com/path?name=value#anchor",
        "http://example.com#section1",
        "https://example.com/path#section2",
        "http://user:pass@example.com",
        "https://user:pass@www.example.com/path",
        "http://example.com/path/to/resource?query=val%20ue",
        "https://example.com/path/to/$resource",
        "http://example.com/path/to/res@urce",
        "https://example.com/path#anchor?with=query",
        "http://example.com/path?name=value&name2=value2",
        "https://example.com/path?name=value&name2=value2&name3=value3",
        "http://example.com/path?name=value#anchor?next=another",
        "http://xn--fsq.com",
        "http://www.xn--fiqs8s.com",
        "http://example.com/path%20with%20spaces/",
        "https://example.com/query?name=%3Cvalue%3E",
        "http://example.com/über/äöüß",
        "http://example.xyz",
        "https://example.photography",
        "http://example.travel",
        "http://example.com:99999",
        "http://example-domain.com",
        "https://example_domain.com",
        "http://sub_domain.example.com",
    ]
    for url in valid_urls:
        assert Validator.is_valid_url(url)

    invalid_urls = [
        "file://localhost/path/to/file",
        "http://192.168.1.1",
        "https://127.0.0.1:8000",
        "ftp://10.0.0.1/resource",
        "ftp://user:pass@192.168.1.1/resource",
        "www.example.com",
        "example.com/path",
        "example.com/path?query=value",
        "https://xn--e1aybc.xn--p1ai",
        "mailto:someone@example.com",
        "mailto:info@sub.domain.com?subject=Test&body=Hello",
        "data:text/plain;base64,SGVsbG8sIFdvcmxkIQ==",
        "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA",
        "file:///C:/path/to/file.txt",
        "file:///Users/username/Desktop/file.txt",
        "file://localhost/path/to/file.txt",
        "ssh://user@hostname:22",
        "sftp://user@hostname:22",
        "telnet://192.0.2.16:80/",
        "http://[2001:db8::1]",
        "https://[2001:db8::1]:8080/path",
        "ftp://[::1]/resource",
        "http://example..com",
        "http:///example.com",
        "https://example.com:-80",
        "http://a.b",
        "http://0.0.0.0",
        "http://localhost",
    ]
    for url in invalid_urls:
        assert Validator.is_valid_url(url) == False

    with raises(AssertionError):
        Validator.is_valid_url(123)


def test_is_valid_email():
    valid_emails = ["simple@example.com",
                    "very.common@example.com",
                    "disposable.style.email.with+symbol@example.com",
                    "other.email-with-hyphen@example.com",
                    "fully-qualified-domain@example.com",
                    "example-indeed@strange-example.com",
                    "admin@mailserver1",
                    "test.email+alex@leetcode.com",
                    "user@sub.example.com",
                    "username@111.222.333.44444",
                    "Abc..123@example.com",]

    for email in valid_emails:
        assert Validator.is_valid_email(email)

    invalid_emails = [
        "plainaddress",
        "@missinglocalpart.com",
        "username@.com.my",
        "username@sub..com",
        "username@-example.com",
        "username@example..com",
        "user@domain..com",
        "username@.com",
        "“user@domain.com",
        "username@domain@domain.com",
        "user@domain,com",
        "user@domain..com",
        "user.name+tag+sorting@example.com`",
        "x@example.com`",
        "user@com`",
        "user@localhost`",
        '"email"@example.com`',
        "user@[IPv6:2001:db8::1]`",
    ]
    for email in invalid_emails:
        assert Validator.is_valid_email(email) == False

    with raises(AssertionError):
        Validator.is_valid_email(1234)


# UTILS.type_check Test
def test_type_match():
    from typing import (List, Set, Dict, Tuple, Union, Any, Iterable, Optional)

    # Simple Types
    assert type_match(5, int)
    assert not type_match(0.5, int)
    assert not type_match(None, int)
    assert not type_match(True, int)

    assert type_match(1.5, float)
    assert not type_match(1, float)
    assert not type_match(None, float)
    assert not type_match(True, float)

    assert type_match("normal string", str)
    assert not type_match(123, str)
    assert not type_match(None, str)
    assert not type_match(True, str)

    assert type_match(b"bytestring", bytes)
    assert not type_match("normal string", bytes)
    assert not type_match(None, bytes)
    assert not type_match(True, bytes)

    assert type_match(False, bool)
    assert type_match(True, bool)
    assert not type_match(1.4, bool)
    assert not type_match(None, bool)

    assert type_match(None, None)
    assert not type_match("Not None", None)
    assert not type_match(True, None)
    assert not type_match(False, None)

    assert type_match((1, 2, 3), tuple)
    assert not type_match([1, 2, 3], tuple)
    assert not type_match(None, tuple)
    assert not type_match(True, tuple)

    assert type_match([1, 2, 3], list)
    assert not type_match((1, 2, 3), list)
    assert not type_match(None, list)
    assert not type_match(True, list)

    assert type_match({"a": 1, "b": 2}, dict)
    assert not type_match({"a", "b", "c"}, dict)
    assert not type_match(None, dict)
    assert not type_match(True, dict)

    assert type_match({"a", "b", "c"}, set)
    assert not type_match({"a": 1, "b": 2}, set)
    assert not type_match(None, set)
    assert not type_match(True, set)

    # Complex Types
    assert type_match([1, 2, 3], List[int])
    assert not type_match([1, "2", 3], List[int])
    assert not type_match("123", List[int])
    assert not type_match(None, List[int])
    assert not type_match(True, List[int])

    # One hint 'int' assumes each item to be int
    assert type_match((1, 2, 3), Tuple[int])
    # Two hints 'int' and 'str' assumes first item to be int and second to be str
    assert type_match((1, "2"), Tuple[int, str])
    assert not type_match(("1", 2), Tuple[int, str])
    assert not type_match(123, Tuple[int, str])
    assert not type_match(None, Tuple[int, str])
    assert not type_match(True, Tuple[int, str])

    assert type_match({"a": 1, "b": 2}, Dict[str, int])
    assert not type_match(123, Dict[str, int])
    assert not type_match({1: 1, "b": 2}, Dict[str, int])
    assert not type_match({"1": "1", "b": 2}, Dict[str, str])
    assert not type_match(None, Dict[str, str])
    assert not type_match(True, Dict[str, str])

    assert type_match({"a", "b", "c"}, Set[str])
    assert not type_match({"a", "b", 123}, Set[int])
    assert not type_match("123", Set[str])
    assert not type_match(None, Set[str])
    assert not type_match(True, Set[str])

    assert type_match("any value", Any)
    assert type_match(123, Any)
    assert type_match(12.3, Any)
    assert type_match(None, Any)
    assert type_match(True, Any)

    assert type_match(["a", "b", "c"], Iterable[str])
    assert not type_match(123, Iterable[str])
    assert not type_match(None, Iterable[str])
    assert not type_match(True, Iterable[str])

    assert type_match("None", Union[int, str, None])
    assert type_match(10, Union[int, str])
    assert type_match("10", Union[int, str])
    assert not type_match(["10", 12], Union[int, str])
    assert not type_match(None, Union[int, str])
    assert not type_match(True, Union[int, str])

    assert type_match(10, Optional[int])
    assert type_match(None, Optional[int])
    assert type_match(("10", 123), Optional[tuple])
    assert not type_match("10", Optional[float])
    assert not type_match("10", Optional[int])
    assert not type_match(True, Optional[int])


def test_type_check():
    @typecheck
    def add(a: float, b: int) -> str:
        return f"{a + b}"

    assert add(1.0, 2) == f"{1.0 + 2}"

    with raises(TypeError):
        add(1, 2)
    with raises(TypeError):
        add("1", "2")

    @typecheck
    def wrong_return() -> str:
        return None
    with raises(TypeError):
        wrong_return()

    # Complex Types
    from typing import Dict, List

    @typecheck
    def complex_types(items: Dict[str, List[int]], return_str=True) -> str:
        return "string" if return_str else 69

    assert complex_types({}) == "string"
    assert complex_types({"key": [1, 2, 3]}) == "string"

    with raises(TypeError):
        complex_types([1, 2, 3])
    with raises(TypeError):
        complex_types("123")
    with raises(TypeError):
        complex_types({1: 1})
    with raises(TypeError):
        complex_types({"1": 1})
    with raises(TypeError):
        complex_types({"1": ["str"]})
    with raises(TypeError):
        complex_types({"1": [1, 2, 3, "str"]})
    with raises(TypeError):
        complex_types({"key": [1, 2, 3,]}, False)

    # Skip test

    @typecheck(skip=['b', 'c'])
    def skip_test(a: int, b: int, c: int):
        return a + b + c

    assert skip_test(1, 3.5, 2.5) == 7
    with raises(TypeError):
        skip_test(1.5, 3.5, 2)

    # Only test
    @typecheck(only=['b'])
    def only_test(a: int, b: int, c: int):
        return a + b + c

    assert only_test(1.5, 3, 2.5) == 7
    with raises(TypeError):
        only_test(1, 3.5, 2)

    # Only Test 2
    try:
        # skip and only are mutually exclusive: Raise AssertionError if both provided
        @typecheck(only=['b'], skip=['a'])
        def only_test_2(a: int, b: int, c: int):
            return a + b + c
    except AssertionError:
        pass


if __name__ == "__main__":
    all_functions = [
        (test_pins, "test_pins"),
        (test_colorize_4bit, "test_colorize_4bit"),
        (test_colorize_8bit, "test_colorize_8bit"),
        (test_colorize_24bit, "test_colorize_24bit"),
        (test_colorize_regex, "test_colorize_regex"),
        (test_create_hr, "test_create_hr"),
        (test_create_status, "test_create_status"),
        (test_boxify, "test_boxify"),
        (test_create_list_ordered, "test_create_list_ordered"),
        (test_create_list_unordered, "test_create_list_unordered"),
        (test_create_table, "test_create_table"),
        (test_promptize, "test_promptize"),
        (test_textalign_x, "test_textalign_x"),
        (test_textalign_y, "test_textalign_y"),
        (test_indent_text, "test_indent_text"),
        (test_splice_text, "test_splice_text"),
        (test_contains_ansi, "test_contains_ansi"),
        (test_shorten_path, "test_shorten_path"),
        (test_now, "test_now"),
        (test_for_each, "test_for_each"),
        (test_format_date, "test_format_date"),
        (test_get_calendar, "test_get_calendar"),
        (test_create_ansi_fmt, "test_create_ansi_fmt"),
        (test__validate_types, "test__validate_types"),
        (test__validate_colors, "test__validate_colors"),
        (test__validate_attrs, "test__validate_attrs"),
        (test__longest_string, "test__longest_string"),
        (test_is_strong_password, "test_is_strong_password"),
        (test_is_valid_extension, "test_is_valid_extension"),
        (test_is_valid_filepath, "test_is_valid_filepath"),
        (test_is_valid_dirpath, "test_is_valid_dirpath"),
        (test_is_valid_ip, "test_is_valid_ip"),
        (test_is_valid_url, "test_is_valid_url"),
        (test_is_valid_email, "test_is_valid_email"),
        (test_type_match, "test_type_match"),
        (test_type_check, "test_type_check"),
    ]

    # Skip these tests
    to_skip = [
        "test_format_date"
    ]

    failed = []
    passed = []
    for func, name in all_functions:
        if name in to_skip:
            print(colored(f"Skipping: {name}()", "light_yellow"))
            print()
            continue

        try:
            func()
            passed.append(name)
        except AssertionError:
            failed.append(name)

    printc(f"Total Tests: {len(all_functions):<3}", "blue", end="\n\n")

    if passed:
        printc(f"Tests Passed: {len(passed):<3}", "green", end=" ")
        printc("."*len(passed), "light_green",  end="\n\n")

    if failed:
        printc(f"Tests Failed: {len(failed):<3}", "red", end=" ")
        printc("."*len(failed), "red")
        for name in failed:
            print("Failed:", colored(f"{name}()", "red"))

    if len(all_functions) - len(to_skip) == len(passed):
        printc("All Tests Passed :)", "light_green")

    if len(all_functions) == len(failed):
        printc("All Tests Failed :(", "light_red")

    # Exit with a code same as failed tests...
    exit(len(failed))
