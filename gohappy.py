import os
import requests
import subprocess
import uuid
from os import path
from os.path import expanduser
from threading import Thread

from PyQt4.QtCore import QThread, pyqtSignal

from gohappygenerics import EventFields, ClientEvents, ServerEvents, ResponseCode, ExplorerEvents, ExplorationResponse
from socketIO_client import BaseNamespace, SocketIO

login_thread = None
register_thread = None


class GoHappy(object):
    HOST = "amirhosein.me"
    PORT = 5000

    BASE_URL = 'http://' + HOST + ':' + str(PORT)
    REGISTER_URL = '/auth/register'
    LOGIN_URL = '/auth/login'

    _instance_counter = 0

    def __init__(self, token, ready_listener=None):
        assert GoHappy._instance_counter == 0
        assert token is not None
        assert ready_listener is None or callable(ready_listener)

        self.is_new_connection_opened = False

        self._is_connected = False
        self._token = token
        self._namespace = None
        self._last_request_code = None

        self._ready_to_operation_listener = ready_listener
        self._new_connection_listener = None
        self._new_exploration_result_listener = None
        self._path_request_listener = None

        GoHappy._instance_counter += 1

        self.socket_thread = SocketThread(self, self.set_namespace, GoHappyNamespace)
        self.socket_thread.start()

    def start_new_connection(self, listen_callback):
        assert callable(listen_callback)
        assert self._is_connected
        assert self._new_connection_listener is None

        self._new_connection_listener = listen_callback
        self._namespace.start_new_connection()

    def start_new_exploration(self, source_username, callback):
        assert callable(callback)
        assert source_username
        assert self.is_new_connection_opened
        assert self._new_exploration_result_listener is None

        self._new_exploration_result_listener = callback
        self._namespace.start_new_exploration(source_username)

    def get_files(self, session_id, pth, callback):
        assert session_id
        assert pth
        assert callable(callback)
        assert self.is_new_connection_opened
        assert self._path_request_listener is None
        assert self._last_request_code is None

        self._path_request_listener = callback
        self._last_request_code = uuid.uuid4().hex

        self._namespace.request_for_files(session_id, pth, self._last_request_code)

    def close_session(self):
        assert self.is_new_connection_opened
        pass

    def release(self):
        self.socket_thread.join()

    def get_token(self):
        return self._token

    def set_token(self, token):
        self._token = token

    def set_namespace(self, namespace):
        assert namespace
        self._namespace = namespace

    def _set_is_connected(self, enable):
        self._is_connected = enable

        if self._ready_to_operation_listener:
            self._ready_to_operation_listener(self)

    def _set_new_connection_established(self, enable):
        self.is_new_connection_opened = enable

    def _on_new_connection(self, is_successful):
        if self._new_connection_listener:
            self._new_connection_listener(is_successful)

            self._new_connection_listener = None

    def _on_start_exploration_result_received(self, result, message, answer, session_id, source):
        if self._new_exploration_result_listener is None:
            return

        is_successful = result is not None and result == ResponseCode.SUCCESSFUL
        is_source_offline = message is not None and message == ExplorationResponse.SOURCE_IS_OFFLINE
        is_permission_denied = answer is not None and answer == ExplorationResponse.ANSWER_PERMISSION_DENIED
        self._new_exploration_result_listener(session_id, is_successful, is_source_offline, is_permission_denied)

        self._new_exploration_result_listener = None

    def _on_files_received(self, result, message, request_code, session_id, data):
        if self._path_request_listener is None:
            return

        is_successful = result is not None \
                        and result == ResponseCode.SUCCESSFUL \
                        and self._last_request_code == request_code
        error = data[0] if len(data) == 2 else None
        data = data[1] if len(data) == 2 else []
        is_source_offline = message is not None and message == ExplorationResponse.SOURCE_IS_OFFLINE
        self._path_request_listener(is_successful, error, data, session_id, is_source_offline)

        self._path_request_listener = None
        self._last_request_code = None

    @staticmethod
    def login(username, password, callback):
        global login_thread

        url = GoHappy.BASE_URL + GoHappy.LOGIN_URL
        data = {'username': username, 'password': password}

        def cb(dt): callback(dt.get(EventFields.RESULT),
                             dt.get(EventFields.MESSAGE),
                             dt.get(EventFields.TOKEN))

        login_thread = HttpRequestWorker(url, data, 'post', cb)
        login_thread.finishSignal.connect(lambda (dt): cb(dt))
        login_thread.start()

    @staticmethod
    def register(username, password, callback):
        global register_thread
        url = GoHappy.BASE_URL + GoHappy.REGISTER_URL
        data = {'username': username, 'password': password}

        def cb(dt): callback(dt.get(EventFields.RESULT),
                             dt.get(EventFields.MESSAGE),
                             dt.get(EventFields.TOKEN),
                             dt.get(EventFields.USER_ID))

        register_thread = HttpRequestWorker(url, data, 'post', cb)
        register_thread.finishSignal.connect(lambda (dt): cb(dt))
        register_thread.start()

    @staticmethod
    def save_token(token):
        assert token
        config_parent_path = path.join(expanduser('~'), '.gohappy')
        config_path = path.join(config_parent_path, 'client.conf')

        if not os.path.exists(config_parent_path):
            os.mkdir(config_parent_path)

        with open(config_path, 'w') as f:
            f.write(token)
            f.close()

    @staticmethod
    def load_token():
        config_path = path.join(expanduser('~'), '.gohappy', 'client.conf')
        try:
            f = open(config_path, 'r')
            token = f.read()
        except:
            return None

        return token.strip()

    @staticmethod
    def get_name(file_info):
        try:
            return file_info[0]
        except:
            return None

    @staticmethod
    def get_path(file_info):
        try:
            return file_info[1]
        except:
            return None

    @staticmethod
    def is_dir(file_info):
        try:
            return file_info[2]
        except:
            return None

    @staticmethod
    def add_client_to_startup():
        home = os.environ["HOME"]

        name = 'GoHappyClient'
        command = os.path.join(os.getcwd(), 'client_auto_start.sh')
        GoHappy.make_executable(command)

        launcher = ["[Desktop Entry]", "Name=", "Exec=", "Type=Application", "X-GNOME-Autostart-enabled=true"]
        dr = home + "/.config/autostart/"
        if not os.path.exists(dr):
            os.makedirs(dr)
        file = dr + name.lower() + ".desktop"

        if not os.path.exists(file):
            with open(file, "wt") as out:
                for l in launcher:
                    l = l + name if l == "Name=" else l
                    l = l + command if l == "Exec=" else l
                    out.write(l + "\n")

    @staticmethod
    def run_client():
        command = os.path.join(os.getcwd(), 'client_auto_start.sh')
        GoHappy.make_executable(command)

        subprocess.Popen([command], shell=True)

    @staticmethod
    def make_executable(path):
        mode = os.stat(path).st_mode
        mode |= (mode & 0o444) >> 2
        os.chmod(path, mode)


class GoHappyNamespace(BaseNamespace):
    _context = None

    def init_with(self, gohappy):
        self._context = gohappy

    def on_connect(self):
        print '\n[connected]'
        self._context._set_is_connected(True)

    def on_disconnect(self):
        print '\n[disconnected]'
        self._context._set_is_connected(False)
        self._context._set_new_connection_established(False)

    def on_event(self, event, *args):
        print '\n[on_' + event + ']'

        if event == ClientEvents.CONNECTION_ESTABLISHED:
            self.handle_new_connection(*args)
        elif event == ExplorerEvents.NEW_EXPLORATION_RESULT:
            self.handle_new_exploration_result(*args)
        elif event == ExplorerEvents.PATH_REQUEST_RESPONSE:
            self.handle_path_request_response(*args)

    def handle_new_connection(self, *args):
        data = args[0]

        if data.get(EventFields.RESULT, ResponseCode.FAILED) == ResponseCode.SUCCESSFUL:
            print "[new connection established]"
            self._context._set_new_connection_established(True)
            self._context._on_new_connection(True)
        else:
            print "[new connection failed]"
            self._context._set_new_connection_established(False)
            self._context._on_new_connection(False)

    def handle_new_exploration_result(self, *args):
        data = args[0]

        self._context._on_start_exploration_result_received(
            data.get(EventFields.RESULT),
            data.get(EventFields.MESSAGE),
            data.get(EventFields.ANSWER),
            data.get(EventFields.SESSION_ID),
            data.get(EventFields.SOURCE)
        )

    def handle_path_request_response(self, *args):
        data = args[0]

        self._context._on_files_received(
            data.get(EventFields.RESULT),
            data.get(EventFields.MESSAGE),
            data.get(EventFields.REQUEST_CODE),
            data.get(EventFields.SESSION_ID),
            data.get(EventFields.RESPONSE_DATA)
        )

    def start_new_connection(self):
        data = {EventFields.TOKEN: self._context.get_token().decode('ascii'),
                EventFields.CLIENT_TYPE: EventFields.EXPLORER}
        self.emit(ServerEvents.NEW_CONNECTION, data)

    def start_new_exploration(self, username):
        self.emit(ServerEvents.NEW_EXPLORATION, {
            EventFields.TOKEN: self._context.get_token().decode('ascii'),
            EventFields.SOURCE: username
        })

    def request_for_files(self, session_id, pth, request_code):
        self.emit(ServerEvents.EXPLORATION_PATH_REQUEST, {
            EventFields.TOKEN: self._context.get_token().decode('ascii'),
            EventFields.SESSION_ID: session_id,
            EventFields.REQUEST_CODE: request_code,
            EventFields.PATH: pth
        })


class SocketThread(Thread):
    def __init__(self, gohappy, callback, namespace):
        super(SocketThread, self).__init__()

        self.daemon = True

        self.gohappy_set_namespace = callback
        self._gohappy = gohappy
        self._ns = namespace

    def run(self):
        socketio = SocketIO(GoHappy.HOST, GoHappy.PORT, transports=['xhr-polling'])

        namespace = socketio.define(self._ns)
        namespace.init_with(self._gohappy)

        self.gohappy_set_namespace(namespace)

        socketio.wait()


class HttpRequestWorker(QThread):
    finishSignal = pyqtSignal(dict)

    def __init__(self, url, data, method, callback):
        super(HttpRequestWorker, self).__init__()
        self.url = url
        self.data = data
        self.method = method
        self.callback = callback

    def run(self):
        r = None
        if self.method.lower() == 'get':
            r = requests.get(self.url, params=self.data)
        elif self.method.lower() == 'post':
            r = requests.post(self.url, data=self.data)

        data = r.json()
        self.finishSignal.emit(data)
        # self.callback(data)
