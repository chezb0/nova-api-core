class FakeLogger:
    def __init__(self):
        self.logs = []

    def info(self, msg, *args, **kwargs):
        self.logs.append(("info", msg))

    def error(self, msg, *args, **kwargs):
        self.logs.append(("error", msg))

    def critical(self, msg, *args, **kwargs):
        self.logs.append(("error", msg))

    def warning(self, msg, *args, **kwargs):
        self.logs.append(("warning", msg))

    def debug(self, msg, *args, **kwargs):
        self.logs.append(("debug", msg))


class FakeDB:
    def __init__(self):
        self.connected = False
        self.disconnected = False

    async def connect(self):
        self.connected = True

    async def disconnect(self):
        self.disconnected = True


class FakeConfig:
    APP_NAME = "Test App"
    DEBUG = True


class FakeBootstrap:
    APP_NAME = "Test App"
    APP_VERSION = "1.0"
    ENV = "dev"
    LOG_LEVEL = "DEBUG"
    LOG_OUTPUT = "CONSOLE"
    LOG_FILE_PATH = None
