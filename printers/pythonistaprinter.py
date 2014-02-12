import console
from .plainprinter import PlainPrinter

indent = ' '

class PythonistaPrinter(PlainPrinter):
	def __init__(self):
		super(PythonistaPrinter, self).__init__()

	def pprint(self, tlist):
		for item in tlist:
			if item.type == 'project' or item.type == 'seq-printer':
				self.project(item)
			elif item.type == 'note':
				self.note(item)
			elif item.type == 'task':
				self.ttask(item)
			elif item.type == 'newline':
				self.newline(item)

	def project(self, item):
		console.set_color(0.00, 0.00, 0.00)
		print(indent * item.indent_level + item.text + ':')
		console.set_color()

	def note(self, item):
		print(indent * item.indent_level + item.text)

	def ttask(self, item):
		self.task(item)
		print(indent * item.indent_level + '- ' + item.text)
		console.set_color()

	def task(self, item):
		if item.has_tag('working'):
			console.set_color(0.00, 0.50, 0.50)
		elif item.has_any_tags(['done', 'blocked']):
			console.set_color(0.50, 0.50, 0.50)
		elif item.has_tag('next'):
			console.set_color(0.00, 0.50, 1.00)
		elif item.has_tag('due'):
			console.set_color(1.00, 0.00, 0.50)

	def newline(self, item):
		print('\n')

