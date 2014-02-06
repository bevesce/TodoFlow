import os

def prind(f):
	for filename in os.listdir(f):
		if os.path.isdir(f + filename):
			if not filename.startswith('archive') and filename != 'workflows':
				prind(f + filename + '/')
		elif not filename.endswith('pyc') and not filename.startswith('.'):
			print (f + filename)[1:]

prind('./')

