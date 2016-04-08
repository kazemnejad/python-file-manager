#!/usr/bin/python

import os
import sys
from PyQt4 import QtGui
from gi.repository import Notify, GdkPixbuf
from os import path
from os.path import expanduser

from tendo import singleton

me = singleton.SingleInstance()

from PyQt4.QtGui import QWidget

from gohappygenerics import PathResult, ClientEvents, SourceEvents, EventFields, ResponseCode, ServerEvents, \
    ExplorationResponse
from socketIO_client import SocketIO, BaseNamespace


class PermissionQuestionDialog:
    def __init__(self, explorer_name):
        self.msg = explorer_name + " wants to modify your files, Are you OK with this?"
        pass

    def ask(self):

        app = QtGui.QApplication(sys.argv)

        w = QWidget()
        reply = QtGui.QMessageBox.question(w, 'Ask for your permission',
                                           self.msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            return True
        else:
            return False


def show_notification(title, body):
    Notify.init("Gohappy client")
    notification = Notify.Notification.new(title, body)

    image = GdkPixbuf.Pixbuf.new_from_file("resources/gohappy.svg")

    notification.set_icon_from_pixbuf(image)
    notification.set_image_from_pixbuf(image)

    return notification.show()


def get_path_result(pth):
    if not os.access(pth, os.R_OK):
        return PathResult.ACCESS_DENIED, []

    if not os.path.exists(pth):
        return PathResult.NOT_FOUND, []

    dirs = os.listdir(pth)
    files = []
    for f in dirs:
        fi = f, os.path.join(pth, f), os.path.isdir(os.path.join(pth, f))
        files.append(fi)

    return None, files


def get_token():
    config_path = path.join(path.expanduser("~"), ".gohappy", "client.conf")
    if not path.exists(config_path):
        return None

    try:
        config = open(config_path, 'r')
        token = config.read()
        config.close()
    except Exception:
        return None
    token = token.strip()
    return token


class Context:
    HOST = "amirhosein.me"
    PORT = 5000

    token = ""
    socketIO = None

    def __init__(self, token=""):
        self.token = token

    def set_token(self, token):
        self.token = token

    def set_socket_io(self, socketio):
        self.socketIO = socketio


cnx = Context()


class Namespace(BaseNamespace):
    def on_disconnect(self):
        print '[DisConnected]'

    def on_connect(self):
        print '[Connected]'
        self.start_new_connection()

    def on_event(self, event, *args):
        print "\non_" + event

        if event == ClientEvents.CONNECTION_ESTABLISHED:
            self.handle_new_connection_established(*args)
        elif event == ClientEvents.SESSION_CLOSED:
            self.handle_session_closed(*args)
        elif event == ClientEvents.SESSION_CLOSE_ERROR:
            pass
        elif event == SourceEvents.ASK_FOR_PERMISSION:
            self.handle_ask_for_permission(*args)
        elif event == SourceEvents.EXPLORATION_STARTED:
            self.handle_exploration_started(*args)
        elif event == SourceEvents.PATH_REQUESTED:
            self.handle_path_request(*args)
        elif event == SourceEvents.PATH_RESPONSE_ERROR:
            self.handle_path_reponse_error(*args)

    def handle_new_connection_established(self, *args):
        data = args[0]

        if data.get(EventFields.RESULT, ResponseCode.FAILED) == ResponseCode.SUCCESSFUL:
            print "[New Connection Established]"
        else:
            self.start_new_connection()

    def start_new_connection(self):
        global cnx

        data = {EventFields.TOKEN: cnx.token.decode('ascii'), EventFields.CLIENT_TYPE: EventFields.SOURCE}
        self.emit(ServerEvents.NEW_CONNECTION, data)

    def handle_ask_for_permission(self, *args):
        global cnx
        data = args[0]

        explorer_username = data.get(EventFields.EXPLORER)
        session_id = data.get(EventFields.SESSION_ID)

        dialog = PermissionQuestionDialog(explorer_username)
        is_ok = dialog.ask()

        answer = ExplorationResponse.ANSWER_PERMISSION_GRANTED if is_ok else ExplorationResponse.ANSWER_PERMISSION_DENIED

        self.emit(ServerEvents.EXPLORATION_PERMISSION_REQUEST_ANSWER, {
            EventFields.SESSION_ID: session_id,
            EventFields.TOKEN: cnx.token,
            EventFields.ANSWER: answer
        })

    def handle_exploration_started(self, *args):
        data = args[0]

        title = "Exploration started!"
        body = "by " + data.get(EventFields.EXPLORER)

        show_notification(title, body)

    def handle_path_request(self, *args):
        global cnx
        data = args[0]

        print data

        request_code = data.get(EventFields.REQUEST_CODE)
        session_id = data.get(EventFields.SESSION_ID)
        requested_path = str(data.get(EventFields.PATH))

        if not requested_path.startswith("/"):
            requested_path = expanduser('~')

        error, files = get_path_result(requested_path)
        pr = PathResult()
        pr.error = error
        pr.result = files

        self.emit(ServerEvents.EXPLORATION_PATH_REQUEST_RESPONSE,
                  {
                      EventFields.TOKEN: cnx.token,
                      EventFields.REQUEST_CODE: request_code,
                      EventFields.SESSION_ID: session_id,
                      EventFields.RESPONSE_DATA: (error, files),
                  })

    def handle_session_closed(self, *args):
        data = args[0]

        title = "Session closed!"
        body = "session id: " + data.get(EventFields.SESSION_ID)

        show_notification(title, body)

    def handle_path_reponse_error(self, *args):
        data = args[0]

        print data


def main():
    global cnx

    token = get_token()
    if token is None:
        print "no valid token found"
        print "exiting..."
        return
    else:
        print "initializing with: " + token

    socketIO = SocketIO(cnx.HOST, cnx.PORT, Namespace)

    cnx.set_token(token)
    cnx.set_socket_io(socketIO)

    socketIO.wait()


if __name__ == "__main__":
    main()
