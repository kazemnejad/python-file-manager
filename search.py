import os
from Queue import Queue, Empty
from threading import Thread, Event

import magic

from util import Log


class StoppableThread(Thread):
    def __init__(self):
        super(StoppableThread, self).__init__()
        self._stop = Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


class SearchThread(StoppableThread):
    def __init__(self, queueFolder, queueFile, target, result):
        super(SearchThread, self).__init__()

        self.foldersQueue = queueFolder
        self.filesQueue = queueFile

        self._target = target
        self._result = result

    def run(self):
        while not self.stopped():
            try:
                item = self.foldersQueue.get(False)
            except Empty:
                # Log.d("folders queue is Empty, skipping...")
                pass
            else:
                self.do_search(item)
                self.foldersQueue.task_done()

        Log.d(self.name, "finished")

    def do_search(self, item):
        if self._target in os.path.basename(item) and not os.path.isfile(item):
            self._result.append((item, os.path.basename(item), None, 1))

        if os.path.basename(item).startswith("."):
            return

        for i in os.listdir(item):
            pth = os.path.join(item, i)
            if os.path.isfile(os.path.join(item, i)):
                self.search_in_filename(pth)
            elif os.path.isdir(os.path.join(item, i)):
                self.search_in_dir_name(pth)

    def search_in_filename(self, pth):
        if self._target in os.path.basename(pth):
            self._result.append((pth, os.path.basename(pth), None, 1))
        else:
            self.filesQueue.put(pth)

    def search_in_dir_name(self, pth):
        self.foldersQueue.put(pth)


class FileSearchThread(StoppableThread):
    def __init__(self, queueFile, target, result):
        super(FileSearchThread, self).__init__()

        self.filesQueue = queueFile
        self._target = target
        self._result = result

    def run(self):
        while not self.stopped():
            try:
                item = self.filesQueue.get(False)
            except Empty:
                # Log.d("files queue is Empty, skipping...")
                pass
            else:
                self.do_search(item)
                self.filesQueue.task_done()

        Log.d(self.name, " finished")

    def do_search(self, item):
        if not magic.from_file(item, mime=True).startswith('text/'):
            return

        Log.d(self.name + ": Searching in file: " + item + " queue size : " + str(self.filesQueue.qsize()))

        with open(item, 'r') as f:
            for line in f:
                if self._target in line:
                    self._result.append((item, os.path.basename(item), None, 0))
                    Log.d('in search file :', os.path.dirname(item))
                    break

        Log.d(self.name + ": Ending search in file: " + item + " queue size : " + str(self.filesQueue.qsize()))


class Searcher(StoppableThread):
    def __init__(self, root_dir, target, result_listener):
        assert callable(result_listener)

        super(Searcher, self).__init__()

        self._root_dir = root_dir
        self._target = target
        self._result_callback = result_listener

    def search(self):
        queueFolder = Queue()
        queueFile = Queue()

        result = []

        if os.path.isfile(self._root_dir):
            queueFile.put(self._root_dir)
        elif os.path.isdir(self._root_dir):
            queueFolder.put(self._root_dir)

        s = []
        for i in range(10):
            t = SearchThread(queueFolder, queueFile, self._target, result)
            t.daemon = True
            t.start()

            s.append(t)

        for i in range(10):
            t = FileSearchThread(queueFile, self._target, result)
            t.daemon = True
            t.start()

            s.append(t)

        queueFolder.join()
        queueFile.join()

        for t in s:
            t.stop()
            t.join()

        self._result_callback(result)


if __name__ == '__main__':
    def callback(result): Log.d("\nResults:");[Log.d(i[0]) for i in result]


    searcher = Searcher(
            os.path.join(os.path.expanduser('~'), 'Desktop'),
            "khar",
            callback
    )
    searcher.search()
