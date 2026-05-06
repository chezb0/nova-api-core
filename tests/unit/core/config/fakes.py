class FakeProvider:
    def __init__(self, data: dict):
        self._data = data

    def load(self) -> dict:
        return self._data
