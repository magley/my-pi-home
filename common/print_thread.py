from threading import Thread, Event
from queue import Queue


class PrintThread():
    thread: Thread
    queue: Queue
    is_unpaused: Event

    def __init__(self):
        self.thread = Thread(target=self._print_thread, daemon=True)
        self.queue = Queue()
        self.is_unpaused = Event()


    def start(self):
        self.thread.start()


    def _print_thread(self):
        while True:
            if self.is_unpaused.wait():
                item = self.queue.get()
                if not self.is_unpaused.is_set():
                    # Got paused since last get - handle item when we unpause
                    self.queue.put(item)
                else:
                    print(item)


    def put(self, item: str, ignore_paused = False):
        # Ignore puts while we're not listening to stdout
        if self.is_unpaused.is_set() or ignore_paused:
            self.queue.put(item)


    def set_paused(self):
        self.is_unpaused.clear()


    def set_unpaused(self):
        self.is_unpaused.set()
