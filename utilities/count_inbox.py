from config import inbox_path

done_tag = ' @done'

def count_inbox():
    with open(inbox_path, "r") as f:
        count = 0
        for line in f:
            if line[0] == '_':
                break
            if line[0] == "-" and (line.find(done_tag) == -1):
                count += 1
        if count:
            print(count)
        else:
            print(" ")

count_inbox()
