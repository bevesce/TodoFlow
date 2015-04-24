"""
Search tasks.

Usage:
    tf.py [-n=<named_query>] [(-a|-o)] [<query>]

Options:
    -n=<named_query>] --named_query=<named_query>]   Name of query stored in config.
    -o --or                                          Join named query and query with OR.
    -a --and                                         Join named query and query with AND [it is default].

"""

import todoflow
import config
import utils
import docopt
color_printer = todoflow.printers.ColorPrinter(indention='  ')


if __name__ == '__main__':
    tasks = todoflow.from_dir(config.tasks_dir_path)
    query = utils.argument_to_query(docopt.docopt(__doc__)) or ''
    utils.print_title(query)
    color_printer(tasks.filter(query))
