import os
from PyQt4 import QtCore
from Queue import Queue, Empty
from threading import Thread, Event

import magic
import re

from PyQt4.QtCore import pyqtSignal

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

        self._pattern = target
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

        # Log.d(self.name, "finished")

    def do_search(self, item):
        score = goHappy_find(self._pattern, os.path.basename(item))
        if score > 0:
            self._result.append((item, os.path.basename(item), True, score))
        if os.path.basename(item).startswith("."):
            return

        for i in os.listdir(item):
            pth = os.path.join(item, i)
            if os.path.isfile(os.path.join(item, i)):
                self.search_in_filename(pth)
            elif os.path.isdir(os.path.join(item, i)):
                self.search_in_dir_name(pth)

    def search_in_filename(self, pth):
        score = goHappy_find(self._pattern, os.path.basename(pth))
        if 'Type' in self._pattern:
            score += 2 if os.path.basename(pth).split('.')[-1] == self._pattern['Type'] else -2
        if 'Kind' in self._pattern:
            score += 2 if magic.from_file(pth, mime=True).startswith(self._pattern['Kind']) else -2
        if score >= 10:
            self._result.append((pth, os.path.basename(pth), False, score))
        else:
            self.filesQueue.put(pth)

    def search_in_dir_name(self, pth):
        self.foldersQueue.put(pth)


class FileSearchThread(StoppableThread):
    def __init__(self, queueFile, target, result):
        super(FileSearchThread, self).__init__()

        self.filesQueue = queueFile
        self._pattern = target
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

        # Log.d(self.name, " finished")

    def do_search(self, item):
        if not magic.from_file(item, mime=True).startswith('text/'):
            return

        # Log.d(self.name + ": Searching in file: " + item + " queue size : " + str(self.filesQueue.qsize()))

        with open(item, 'r') as f:
            for line in f:
                score = goHappy_find(self._pattern, line)
                if score >= 10:
                    self._result.append((item, os.path.basename(item), False, score))
                    Log.d('in search file :', os.path.dirname(item))
                    break

        # Log.d(self.name + ": Ending search in file: " + item + " queue size : " + str(self.filesQueue.qsize()))


class Searcher(QtCore.QThread):
    updateSignal = pyqtSignal(list)

    def __init__(self, root_dir, pattern, result_listener):
        assert callable(result_listener)

        super(Searcher, self).__init__()

        self._root_dir = root_dir
        self._pattern = goHappy_pattern(pattern)
        self._result_callback = result_listener

    def search(self):
        self.start()

    def run(self):
        queueFolder = Queue()
        queueFile = Queue()

        result = []

        if os.path.isfile(self._root_dir):
            queueFile.put(self._root_dir)
        elif os.path.isdir(self._root_dir):
            queueFolder.put(self._root_dir)

        s = []
        for i in range(10):
            t = SearchThread(queueFolder, queueFile, self._pattern, result)
            t.daemon = True
            t.start()

            s.append(t)

        for i in range(10):
            t = FileSearchThread(queueFile, self._pattern, result)
            t.daemon = True
            t.start()

            s.append(t)

        queueFolder.join()
        queueFile.join()

        for t in s:
            t.stop()
            t.join()

        self.updateSignal.emit(result)


def goHappy_regex(line):
    typeObject = re.match(r'(type:)(.*)', line)
    if typeObject:
        type = typeObject.group(2)
    bayadObject = re.match(r'(.*) && (.*)', line)
    if bayadObject:
        vajeb = bayadObject.group(1)
        haroom = bayadObject.group(2)
    patern = r'(' + vajeb + ')+(?!' + haroom + ')+' + '(.*)\.' + '(' + type + ')'
    return patern


# (salam)+(?!hulu)+?

def goHappy_pattern(pattern):
    helplist = ['vajeb', 'haroom', 'mostahab']
    lst = pattern.split("||")
    targets = {}
    for i in xrange(len(lst)):
        lst[i] = lst[i].strip()
        if len(lst[i]) == 0:
            targets[helplist[i]] = []
            continue
        if 'Type:' in lst[i]:
            targets['Type'] = lst[i].split(':')[1]
        elif 'Kind:' in lst[i]:
            targets['Kind'] = lst[i].split(':')[1]
        else:
            targets[helplist[i]] = lst[i].split("&&")
    return targets


def goHappy_find(goHappyPattern, line):
    listOfScore = {'vajeb': 10, 'haroom': -10, 'mostahab': 5,}
    score = 0
    for i in goHappyPattern.get('vajeb', []):
        if i in line:
            score += listOfScore['vajeb']
    for i in goHappyPattern.get('haroom', []):
        if i in line:
            score += listOfScore['haroom']
    for i in goHappyPattern.get('mostahab', []):
        if i in line:
            score += listOfScore['mostahab']

    return score


if __name__ == '__main__':
    def callback(result): Log.d("\nResults:");[Log.d(str(i)) for i in result]


    searcher = Searcher(
            os.path.join(os.path.expanduser('~'), 'Desktop'),
            "khar",
            callback
    )
    searcher.search()
    # s = ' || ne1 && ne2 ||  || Type:txt'
    # print goHappy_pattern(s)
