import todoflow
from todoflow.parser import parse


t = parse("""a
\tb
\t\tc
\t\t\td
""")


class C:
    def __init__(self, a):
        self.a = a

    def f(self, x):
        print(self.a, x)

    def __bool__(self):
        return self.a == 1

if C(1):
    print(1)

if C(2):
    print(2)