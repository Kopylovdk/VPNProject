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


class TariffDoesNotExist(ProcessException):
    """Tariff does not exist"""


class DemoKeyExist(ProcessException):
    """User already have demo key"""


class BelongToAnotherUser(ProcessException):
    """VPN Token belongs to another user"""


class VPNServerResponseError(ProcessException):
    """Error in response from Outline client"""


class VPNTokenDoesNotExist(ProcessException):
    """VPN Token does not exist"""


class TransportMessageSendError(ProcessException):
    """Send message with transport error"""
