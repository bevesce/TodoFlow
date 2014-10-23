"""
Print out agenda.

Usage:
    agenda.py [-n=<named_query>] [(-a|-o)] [<query>]

Options:
    -n=<named_query>] --named_query=<named_query>]   Name of query stored in config.
    -o --or                                          Join named query and query with OR.
    -a --and                                          Join named query and query with AND [it is default].

"""
import docopt
import todoflow
import utils
from config import tasks_path

color_printer = todoflow.printers.ColorPrinter(indention='    ')
due_printer = todoflow.printers.CountdownPrinter('@due')
date_printer = todoflow.printers.CountdownPrinter('@date')


if __name__ == '__main__':
    tasks = todoflow.from_path(tasks_path)
    query = utils.argument_to_query(docopt.docopt(__doc__))
    if query:
        tasks = tasks.filter(query)
        print query
        utils.print_divider()

    utils.print_title('due', todoflow.colors.on_red)
    due_printer(tasks)
    utils.print_divider()

    utils.print_title('date', todoflow.colors.on_magenta)
    date_printer(tasks)
    utils.print_divider()

    utils.print_title('working', todoflow.colors.on_green)
    color_printer(tasks.filter('@working and not @done'))
    utils.print_divider()

    utils.print_title('next', todoflow.colors.on_blue)
    color_printer(tasks.filter('@next and not @done'))
