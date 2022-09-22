from sanic.exceptions import SanicException

from sanic_ext.extensions.health.endpoint import setup_health_endpoint

from ..base import Extension
from .monitor import HealthMonitor


class HealthExtension(Extension):
    name = "health"
    MIN_VERSION = (22, 9)

    def startup(self, bootstrap) -> None:
        if self.config.HEALTH:
            if self.config.HEALTH_MONITOR:
                if self.MIN_VERSION > bootstrap.sanic_version:
                    min_version = ".".join(map(str, self.MIN_VERSION))
                    sanic_version = ".".join(map(str, bootstrap.sanic_version))
                    raise SanicException(
                        f"Health monitoring only works with Sanic "
                        f"v{min_version} and above. It looks like you are "
                        f"running {sanic_version}."
                    )
                HealthMonitor.setup(self.app)

            if self.config.HEALTH_ENDPOINT:
                setup_health_endpoint(self.app)

    def included(self):
        return self.config.HEALTH
