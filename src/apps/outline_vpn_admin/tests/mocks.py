class MockResponseCreateKey:

    def __init__(self, outline_id: int = 9999):
        self.status_code = 201
        self.outline_id = outline_id

    def json(self):
        return {
            "id": self.outline_id,
            "name": "test",
            "password": "test",
            "port": 7000,
            "method": "test",
            "accessUrl": "test",
        }


class MockResponseStatusCode204:
    def __init__(self):
        self.status_code = 204


class MockResponseStatusCode404:
    def __init__(self):
        self.status_code = 404


class MockResponseStatusCode200:
    def __init__(self):
        self.status_code = 200


class MockResponseGetServerInfo:
    def __init__(self):
        self.status_code = 200

    def json(self):
        return {
            "name": "My Server",
            "serverId": "7fda0079-5317-4e5a-bb41-5a431dddae21",
            "metricsEnabled": False,
            "createdTimestampMs": 1536613192052,
            "version": "1.0.0",
            "accessKeyDataLimit": {"bytes": 8589934592},
            "portForNewAccessKeys": 1234,
            "hostnameForAccessKeys": "example.com"
        }