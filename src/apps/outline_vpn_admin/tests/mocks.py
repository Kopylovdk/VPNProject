class MockResponseCreateKey:

    def __init__(self):
        self.status_code = 201

    def json(self):
        return {
            "id": 123,
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

