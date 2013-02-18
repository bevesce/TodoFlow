from config import active_lists_path
import os


def activate(filepath):
    if not os.path.lexists(filepath):
        print "File doesn't exists\n" + filepath
        return

    try:
        f = open(active_lists_path, 'r')
    except IOError:
        open(active_lists_path, 'w').close()
        f = open(active_lists_path, 'r')
    finally:
        if filepath in f.read():
            print "Project already active " + filepath.split('/')[-1]
            return

    with open(active_lists_path, 'a') as f:
        f.write(filepath + '\n')
        print 'Activated ' + filepath.split('/')[-1]


def deactivate(filepath):
    line_to_putback = []
    with open(active_lists_path, 'r') as f:
        for line in f:
            if line.strip() != filepath:
                line_to_putback.append(line)
    with open(active_lists_path, 'w') as f:
        f.writelines(line_to_putback)
        print 'Deactivated ' + filepath.split('/')[-1]


def list_active():
    with open(active_lists_path, 'r') as f:
        return [line.strip() for line in f]
