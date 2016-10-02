import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import subprocess


class TestRunner(FileSystemEventHandler):
    def on_any_event(self, event):
        try:
            print(subprocess.check_output(['python3', 'tests/test_parsing.py']).decode('utf-8'))
            print(subprocess.check_output(['python3', 'tests/test_querying.py']).decode('utf-8'))
            print(subprocess.check_output(['python3', 'tests/test_textutils.py']).decode('utf-8'))
            print(subprocess.check_output(['python3', 'tests/test_todos.py']).decode('utf-8'))
        except:
            pass


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    path = '.'
    event_handler = TestRunner()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
