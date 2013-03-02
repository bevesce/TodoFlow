"""change 1 to 0, and 0 to 1"""

from config import should_print_path as should_print

current = int(open(should_print).read())
with open(should_print, 'w') as f:
    f.write(
        str(current ^ 1)
        )
