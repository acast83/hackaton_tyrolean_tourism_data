from http import HTTPStatus as status


class BaseHttpException(Exception):
    _status = status.BAD_REQUEST

    def __init__(self, message: str = '', id_message: str = None, status: int = status.BAD_REQUEST, **kwargs):
        self.message = message
        self.id_message = id_message

        BaseHttpException._status = status
        self._status = int(status)

        self.kwargs = kwargs

    def status(self):
        return self._status

    def _dict(self):
        r = {}
        if self.message:
            r.update({'message': self.message})
        if self.id_message:
            r.update({'id': self.id_message})
        if self._status:
            r.update({'code': self._status})

        for arg in self.kwargs:
            r.update({arg: self.kwargs[arg]})

        return r


class General4xx(BaseHttpException):
    """
    Exception class which is used for HTTP Error 400 - Bad Request.
    """
    _status = status.BAD_REQUEST

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._status = status.BAD_REQUEST


class HttpErrorUnauthorized(BaseHttpException):
    """
    Exception class which is used for HTTP Error 401 - Unauthorized.
    """
    _status = status.UNAUTHORIZED

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._status = status.UNAUTHORIZED


class HttpErrorNotFound(BaseHttpException):
    """
    Exception class which is used for HTTP Error 404 - Not Found.
    """
    _status = status.NOT_FOUND

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._status = status.NOT_FOUND


class HttpErrorExpired(BaseHttpException):
    """
    Exception class which is used for HTTP Error 410 - Not Found.
    """
    _status = status.GONE

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._status = status.GONE


class HttpNotAcceptable(BaseHttpException):
    """
    Exception class which is used for HTTP Error 406 - Not Acceptable.
    """
    _status = status.NOT_ACCEPTABLE

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._status = status.NOT_ACCEPTABLE


class HttpForbiden(BaseHttpException):
    """
    Exception class which is used for HTTP Error FORBIDDEN.
    """
    _status = status.FORBIDDEN

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._status = status.FORBIDDEN


class HttpInvalidParam(BaseHttpException):
    """
    Exception class which is used for HTTP Error 400 - Bad Request.

    Unlike the General4xx Class, this Exception is raised when a parameter was found by Base to have the wrong type or value.
    """
    _status = status.BAD_REQUEST

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._status = status.BAD_REQUEST


class HttpInternalServerError(BaseHttpException):
    """
    Exception class which is used for HTTP Error 500 - Internal Server Error.
    """
    _status = status.INTERNAL_SERVER_ERROR

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._status = status.INTERNAL_SERVER_ERROR


class Documentation(BaseHttpException):
    """
    Exception class which is used for API Dcocumentation
    """
    _status = status.OK

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._status = status.OK

