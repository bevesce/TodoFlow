import inspect
import os

import config


def get_terminal_size():
    # Based on http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
    import os
    env = os.environ

    def ioctl_GWINSZ(fd):
        try:
            import fcntl
            import termios
            import struct
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
        except:
            return
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))
    return int(cr[1]), int(cr[0])


width = get_terminal_size()[0]


def argument_to_query(arguments):
    query = arguments['<query>']
    named_query_name = arguments['--named_query']
    join = _choose_join(arguments)
    named_query = _retrieve_named_query(named_query_name)
    if query and named_query_name:
        return join.join([named_query, query])
    elif query:
        return query
    elif named_query:
        return named_query


def _choose_join(arguments):
    join = ' and '
    if arguments['--or']:
        join = ' or '
    return join


def _retrieve_named_query(named_query_name):
    return config.named_queries.get(named_query_name, '')


def print_title(title, color=None):
    s = '_'
    prefix = s * ((width - len(title)) / 2)
    text = prefix + title
    suffix = (width - len(text)) * s
    print text + suffix
    print ''


def print_divider():
    print ''


def get_base_path():
    return os.path.dirname(
        os.path.abspath(
            inspect.getfile(
                inspect.currentframe()
            )
        )
    )
