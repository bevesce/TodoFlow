import todoflow

def propagate_tag(item, tag, param=None):
	item.tag(tag, param=param)
	for item in item.sublist:
		propagate_tag(item, tag, param)

t = todoflow.all_lists()
for item in t.search('done'):
	propagate_tag(item, 'done')
todoflow.save(t)
