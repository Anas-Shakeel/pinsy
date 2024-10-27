""" 
## Pinsy (Prints & Inputs & ANSI)

A lightweight `Helper` Package to speed up the workflow of creating 
command-line applications.

```
# Usage Example
>> from pinsy import Pins
>> pins = Pins(prompt_char="$")

>> # Taking integer input
>> pins.input_int()
$ Enter an integer: 1

>> # Taking string input
>> pins.input_str()
$ Enter a string: python


>> # Printing warning message
>> pins.print_warning("This is a warning message.")
[*] This is a warning message.

>> # Printing an error message
>> pins.print_error("This is an error message.")
[!] This is an error message.

```


Written By : `Anas Shakeel`
Source Code: `https://www.github.com/Anas-Shakeel/pinsy`
"""

from ._pinsy import Pins, Batched, JsonHighlight, Typewriter, Box, Validator, RevealText