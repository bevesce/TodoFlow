"""
Module contains:

1. Constants like RED, BLUE, ON_RED, RED_ON_BLUE, GREEN_ON_BLUE
that are ascii codes in text that can be used to make terminal output
colorful.

>>> print colors.RED + 'this will be red'

2. Functions like red(text), blue(text), on_red(text), red_on_blue(text), green_on_blue(text).
Using functions in contrary to using constant will append default color escape sequence
so the color will be back to normal after printing text.

>>> print red('this will be red'), 'and this will be in default color'

"""
# constant and functions are generated dynamically
from __future__ import unicode_literals

def seq(code):
    return '\033[{}m'.format(code)

defc_code = default_code = 0
DEFAULT = DEFC = seq(defc_code)

foreground_codes = {
    'red': 31,
    'green': 32,
    'gray': 30,
    'blue': 34,
    'yellow': 33,
    'magenta': 35,
    'cyan': 36,
    'white': 37,
    'crimson': 38,
}
background_codes = {
    'red': 41,
    'green': 42,
    'brown': 43,
    'blue': 44,
    'magenta': 45,
    'cyan': 46,
    'gray': 47,
    'crimson': 48,
    'crimson': 49,
    'crimson': 50,   
}

import sys

_colors = sys.modules[__name__]
def conditional_defc(text):
    if text.endswith(DEFC):
        return text
    return text + DEFC

def make_coloriser(name, color_seq):
    setattr(_colors, name, lambda t: color_seq + conditional_defc(t))
    setattr(_colors, name.upper(), color_seq)


def make_colorisers_from_codes(codes, name_prefix='', seq_prefix=''):
    for k, v in codes.iteritems():
        color_seq = seq_prefix + seq(v)
        make_coloriser(name_prefix + k, color_seq)

make_colorisers_from_codes(foreground_codes)
make_colorisers_from_codes(background_codes, name_prefix='on_')
for fk, fv in foreground_codes.iteritems():
    color_seq = seq(fv)
    make_colorisers_from_codes(
        background_codes, 
        name_prefix=fk + '_on_', 
        seq_prefix=color_seq
    )
