class ProcessException(Exception):
    """Базовое исключение"""
    message = 'BASE_EXCEPTION'

    def __init__(self, message):
        self.message = message


class UserDoesNotExist(ProcessException):
    """User does not exist"""
    # message = 'USER_DOES_NOT_EXIST'


class TransportDoesNotExist(ProcessException):
    """Transport does not exist"""
    # message = 'BOT_DOES_NOT_EXIST'


class VPNServerDoesNotExist(ProcessException):
    """VPNServer does not exist"""
    # message = 'VPN_SERVER_DOES_NOT_EXIST'
