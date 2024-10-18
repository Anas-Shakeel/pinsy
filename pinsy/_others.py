from __future__ import annotations

from typing import Literal, Callable
import re

# Data
ERROR_HANDLING: list = [
    "callback",
    "quit",
    "raise",
]

CONSTRAINTS: list = [
    "only_alpha",
    "only_digits",
    "only_alnum",
]

REGEX_PATTERNS = {
    "email": re.compile(r"^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$", re.IGNORECASE),

    # diegoperini created this url regex
    # https://gist.github.com/dperini/729294
    "url": re.compile(r"^(?:(?:(?:https?|ftp):)?\/\/)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z0-9\u00a1-\uffff][a-z0-9\u00a1-\uffff_-]{0,62})?[a-z0-9\u00a1-\uffff]\.)+(?:[a-z\u00a1-\uffff]{2,}\.?))(?::\d{2,5})?(?:[/?#]\S*)?$", re.IGNORECASE),

    # Pattern taken from https://stackoverflow.com/a/72686232
    "password": re.compile(r'^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*\W)(?!.* ).{8,500}$'),
    "json_keys": re.compile(r'(\".+?\"):'),
    "json_str_values": re.compile(r': (\".+?\")'),
    "json_num_values": re.compile(r': (\d+\.?\d+)'),
    "json_arrays": re.compile(r": \[((?:\s*?(?:.*?),*)*)\s*\]", (re.MULTILINE | re.DOTALL))
}


# Menu heading characters
CHARSETS = {
    "ascii": {
        "TOP_LEFT": "+",
        "BOTTOM_LEFT": "+",
        "TOP_RIGHT": "+",
        "BOTTOM_RIGHT": "+",
        "NORMAL": "-",
        "TOP_ST": "-",
        "BOTTOM_ST": "-",
        "VERTICAL": "|",
        "LEFT_V": "|",
        "RIGHT_V": "|"
    },
    "box": {
        "TOP_LEFT": "┌",
        "BOTTOM_LEFT": "└",
        "TOP_RIGHT": "┐",
        "BOTTOM_RIGHT": "┘",
        "NORMAL": "─",
        "TOP_ST": "─",
        "BOTTOM_ST": "─",
        "VERTICAL": "│",
        "LEFT_V": "│",
        "RIGHT_V": "│"
    },
    "box_round": {
        "TOP_LEFT": "╭",
        "BOTTOM_LEFT": "╰",
        "TOP_RIGHT": "╮",
        "BOTTOM_RIGHT": "╯",
        "NORMAL": "─",
        "TOP_ST": "─",
        "BOTTOM_ST": "─",
        "VERTICAL": "│",
        "LEFT_V": "│",
        "RIGHT_V": "│"
    },
    "box_heavy": {
        "TOP_LEFT": "┏",
        "BOTTOM_LEFT": "┗",
        "TOP_RIGHT": "┓",
        "BOTTOM_RIGHT": "┛",
        "NORMAL": "━",
        "TOP_ST": "━",
        "BOTTOM_ST": "━",
        "VERTICAL": "┃",
        "LEFT_V": "┃",
        "RIGHT_V": "┃"
    },
    "box_double": {
        "TOP_LEFT": "╔",
        "BOTTOM_LEFT": "╚",
        "TOP_RIGHT": "╗",
        "BOTTOM_RIGHT": "╝",
        "NORMAL": "═",
        "TOP_ST": "═",
        "BOTTOM_ST": "═",
        "VERTICAL": "║",
        "LEFT_V": "║",
        "RIGHT_V": "║"
    },
    "blocks": {
        "TOP_LEFT": "▛",
        "BOTTOM_LEFT": "▙",
        "TOP_RIGHT": "▜",
        "BOTTOM_RIGHT": "▟",
        "NORMAL": "■",
        "TOP_ST": "▔",
        "BOTTOM_ST": "▁",
        "VERTICAL": "|",
        "LEFT_V": "▏",
        "RIGHT_V": "▕",
    }
}


# TYPE HINTS START FROM HERE....
Callback = Callable[[str], None]

ErrorHandling = Literal[
    "callback",
    "quit",
    "raise",
]

StrConstraint = Literal[
    "only_alpha",
    "only_digits",
    "only_alnum",
]

PromptChar = Literal[
    "$",
    ">",
    ">>",
    ">>>",
]

Charset = Literal[
    "ascii",
    "box",
    "box_round",
    "box_heavy",
    "box_double",
    "blocks"
]


# Alignments
XAlign = Literal[
    "left",
    "center",
    "right",
]

YAlign = Literal[
    "top",
    "center",
    "bottom",
]


# Fill Character
FillChar = Literal[
    '-',
    '─',
    '━',
    '═',
    '■',
    '█',
    '░',
    '▒',
    '▓',
    '➔',
    '➞',
    '◀',
    '▶',
    '▲',
    '▼',
    '◉',
    '◈'
]

# Bullet Characters
Bullet = Literal[
    '-',
    '+',
    '╼',
    '>',
    '»',
    '➔',
    '❯',
    '▶',
    '➥',
    '➤',
    '·',
    '•',
    '◉',
    '●',
    '■',
    '◈',
    '✓',
    '✔ ',
    '🞬',
    '✗',
    '✕',
    '✘',
    '✚',
    '❖',
    '✸',
    '✦',
    '✩',
    '✭',
    '🟊',
    '✪',
    '🞅',
    '🞇',
    '🞉',
    '🟂',
    '◆',
    '⮚',
    '☑',
    '☒',
    '♥',
]
