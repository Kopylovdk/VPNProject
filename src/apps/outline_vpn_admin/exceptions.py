class ProcessException(Exception):
    """Базовое исключение"""
    message = 'BASE_EXCEPTION'

    def __init__(self, message):
        self.message = message


class UserDoesNotExist(ProcessException):
    """User does not exist"""


class TransportDoesNotExist(ProcessException):
    """Transport does not exist"""


class VPNServerDoesNotExist(ProcessException):
    """VPNServer does not exist"""


class DemoKeyExist(ProcessException):
    """User already have demo key"""
