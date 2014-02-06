import todoflow
from todoflow.printers import PythonistaPrinter
import sys
q = ' '.join(sys.argv[1:])
q = todoflow.expand_query(q)
print q
t = todoflow.all_lists().filter(q)
PythonistaPrinter().pprint(t)
