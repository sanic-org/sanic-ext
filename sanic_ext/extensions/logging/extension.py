from sanic.exceptions import SanicException

from ..base import Extension
from .logger import Logger


class LoggingExtension(Extension):
    name = "logging"
    MIN_VERSION = (22, 9)

    def startup(self, bootstrap) -> None:
        if self.included():
            if self.MIN_VERSION > bootstrap.sanic_version:
                min_version = ".".join(map(str, self.MIN_VERSION))
                sanic_version = ".".join(map(str, bootstrap.sanic_version))
                raise SanicException(
                    f"The logging extension only works with Sanic "
                    f"v{min_version} and above. It looks like you are "
                    f"running {sanic_version}."
                )
            Logger.setup(self.app)

    def included(self):
        return self.config.LOGGING
