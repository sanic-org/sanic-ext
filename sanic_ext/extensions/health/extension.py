from sanic.exceptions import SanicException

from ..base import Extension
from .monitor import HealthMonitor


class HealthExtension(Extension):
    name = "health"
    MIN_VERSION = (22, 9)

    def startup(self, bootstrap) -> None:
        if self.config.HEALTH:
            # TODO:
            # - ADD config values
            if self.MIN_VERSION > bootstrap.sanic_version:
                min_version = ".".join(map(str, self.MIN_VERSION))
                sanic_version = ".".join(map(str, bootstrap.sanic_version))
                raise SanicException(
                    f"Health monitoring only works with Sanic v{min_version} "
                    f"and above. It looks like you are "
                    f"running {sanic_version}."
                )
            HealthMonitor.setup(self.app)
