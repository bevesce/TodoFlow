import todoflow as tf
r = []
t = open('/Users/piotrwilczynski/Dropbox/notes/@ordergroup cloud.taskpaper').read().decode('utf-8')
q = tf.from_text(t)
# for i in q.search('@done'):
#     print i, i.start, i.end
#     r.append((i.start, i.end))

for i in q.filter('@done'):
    print i, i.start, i.end
    r.append((i.start, i.end))


def calculate_ranges_to_fold(document_length, ranges_not_to_fold):
    range_start = 0
    ranges = []

    if ranges_not_to_fold[0][0] == 0:
        range_start = ranges_not_to_fold[0][1]
        ranges_not_to_fold = ranges_not_to_fold[1:]

    for s, e in ranges_not_to_fold:
        if range_start + 1 == s:
            range_start = e
            continue
        ranges.append((range_start + 1, s - 1))
        range_start = e
    if e != document_length:
        ranges.append((e + 1, document_length - 1))
    return ranges

print calculate_ranges_to_fold(len(t), r)
