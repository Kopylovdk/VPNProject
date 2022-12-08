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
