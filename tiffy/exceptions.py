__author__ = 'Liam Costello'


class InvalidArgumentsError(Exception):
    pass


class TypeformError(Exception):
    def __init__(self, token, message, status_code):
        super(TypeformError, self).__init__(
            'Typeform returned the following error: {}'.format(message)
        )
        self.status_code = status_code
        self.message = message
        self.token = token