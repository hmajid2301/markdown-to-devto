class HTTPException(Exception):
    """Basic exception"""


class HTTPAuthException(HTTPException):
    def __init__(self, msg):
        self.msg = "Unable to authenticate request, check `DEVTO_API_KEY`."
        super().__init__(msg)


class HTTPBadRequestException(HTTPException):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(msg)


class HTTPServerException(HTTPException):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(msg)


class HTTPConnectionException(HTTPException):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(msg)
