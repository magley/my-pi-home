def _code_sequence(color: int):
    return f'\033[{color};22;22m'


_COLOR_SEQ_PREF = {
    'BLACK': _code_sequence(30),  # Bad visibility
    'RED': _code_sequence(31),
    'GREEN': _code_sequence(32),
    'YELLOW': _code_sequence(33),
    'BLUE': _code_sequence(34),
    'MAGENTA': _code_sequence(35),
    'CYAN': _code_sequence(36),
    'WHITE': _code_sequence(37),
    'BRIGHT_BLACK': _code_sequence(90),
    'BRIGHT_RED': _code_sequence(91),
    'BRIGHT_GREEN': _code_sequence(92),
    'BRIGHT_YELLOW': _code_sequence(93),
    'BRIGHT_BLUE': _code_sequence(94),
    'BRIGHT_MAGENTA': _code_sequence(95),
    'BRIGHT_CYAN': _code_sequence(96),
    'BRIGHT_WHITE': _code_sequence(97),
}


_COLOR_ESCAPE = '\033[0m'


def colorize(item: str, color: str):
    return f'{_COLOR_SEQ_PREF[color]}{item}{_COLOR_ESCAPE}'


def available_colors():
    keys = list(_COLOR_SEQ_PREF.keys())
    keys.pop(keys.index('BLACK'))
    keys.pop(keys.index('WHITE'))
    return keys
