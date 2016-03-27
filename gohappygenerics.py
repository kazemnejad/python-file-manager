class ServerEvents:
    NEW_CONNECTION = "ask_for_new_connection"
    DISCONNECT = "disconnect"

    NEW_EXPLORATION = "start_new_exploration"
    EXPLORATION_PERMISSION_REQUEST_ANSWER = "permission_answer"
    EXPLORATION_PATH_REQUEST = "path_request"
    EXPLORATION_PATH_REQUEST_RESPONSE = "path_request_response"
    CLOSE_SESSION = "close_session"


class ClientEvents:
    SESSION_CLOSED = "session_closed"
    SESSION_CLOSE_ERROR = "close_session_error"
    CONNECTION_ESTABLISHED = "new_connection_established"


class ExplorerEvents:
    NEW_EXPLORATION_RESULT = "start_new_exploration_result"
    PATH_REQUEST_RESPONSE = "path_request_response"


class SourceEvents:
    ASK_FOR_PERMISSION = "ask_for_permission"
    EXPLORATION_STARTED = "exploration_started"
    PATH_REQUESTED = "source_path_requested"
    PATH_RESPONSE_ERROR = "path_request_response_error"


class ResponseCode:
    SUCCESSFUL = 0
    FAILED = 1

    BAD_REQUEST = 3


class AuthenticationResponse:
    UN_AUTHENTICATED_USER = 30
    INVALID_SOURCE = 31
    PERMISSION_DENIED = 32


class ExplorationResponse:
    SOURCE_IS_OFFLINE = 40
    EXPLORER_IS_OFFLINE = 41

    ANSWER_PERMISSION_GRANTED = 41
    ANSWER_PERMISSION_DENIED = 42

    INVALID_ANSWER = 43
    INVALID_SESSION = 44


class EventFields:
    USER_ID = 'id'
    ANSWER = "answer"
    RESULT = "result"
    MESSAGE = "message"

    TOKEN = "token"
    SESSION_ID = "session_id"
    SOURCE = "source"
    EXPLORER = "explorer"

    REQUEST_CODE = "request_code"
    RESPONSE_DATA = "response_data"
    PATH = "path"

    CLIENT_TYPE = "client_type"


class AuthResponceCode:
    SUCCESS = 10
    FAIL = 11
    USER_EXISTS = 12

    INVALID_CREDENTIALS = 13


class PathResult:
    ACCESS_DENIED = 50
    NOT_FOUND = 51
