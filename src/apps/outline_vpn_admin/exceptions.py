class ProcessException(Exception):
    """Базовое исключение"""
    def __init__(self, message=None):
        self.message = message


class UserDoesNotExist(ProcessException):
    """User does not exist"""


class TransportDoesNotExist(ProcessException):
    """Transport does not exist"""


class VPNServerDoesNotExist(ProcessException):
    """VPNServer does not exist"""


class VPNServerDoesNotResponse(ProcessException):
    """VPNServer does not response on get request"""


class TariffDoesNotExist(ProcessException):
    """Tariff does not exist"""


class DemoKeyExist(ProcessException):
    """User already have demo key"""


class DemoKeyNotAllowed(ProcessException):
    """Can not create demo key"""


class BelongToAnotherUser(ProcessException):
    """VPN Token belongs to another user"""


class VPNServerResponseError(ProcessException):
    """Error in response from Outline client"""


class VPNTokenDoesNotExist(ProcessException):
    """VPN Token does not exist"""


class TransportMessageSendError(ProcessException):
    """Send message with transport error"""
