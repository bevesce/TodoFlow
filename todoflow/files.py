def write(path, text):
    text = text.encode('utf-8')
    with open(path, 'w') as f:
        f.write(text)
