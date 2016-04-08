from threading import Lock


class Log:
    _lock = Lock()

    @staticmethod
    def d(*args):
        Log._lock.acquire()
        print ' '.join(args)
        Log._lock.release()
