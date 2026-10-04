from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("nova-api-core")
except PackageNotFoundError:  # running from source without installation
    __version__ = "0.0.0"
