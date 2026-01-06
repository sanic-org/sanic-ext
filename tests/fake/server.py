from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sanic import Request, Sanic, text
from sanic.log import LOGGING_CONFIG_DEFAULTS, logger

from sanic_ext import Extend


LOGGING_CONFIG = {**LOGGING_CONFIG_DEFAULTS}
LOGGING_CONFIG["formatters"]["generic"]["format"] = "%(message)s"
LOGGING_CONFIG["loggers"]["sanic.root"]["level"] = "DEBUG"


@dataclass
class Config:
    database_url: str = "postgres://localhost/test"


@dataclass
class Service:
    config: Config

    @classmethod
    def create(cls, config: Config):
        return cls(config=config)


class SimpleService:
    value: str = "simple"


class Alpha:
    pass


class Beta:
    def __init__(self, alpha: Alpha) -> None:
        self.alpha = alpha


class Gamma:
    def __init__(self, beta: Beta, request: Optional[Request] = None) -> None:
        self.beta = beta
        self.request = request


class RequestDependent:
    def __init__(self, request: Request):
        self.request = request


class CircularA:
    def __init__(self, b: CircularB) -> None:
        self.b = b


class CircularB:
    def __init__(self, a: CircularA) -> None:
        self.a = a


app = Sanic("FakeServer", log_config=LOGGING_CONFIG)
app.config.MY_CONSTANT = "constant_value"
Extend(app)
app.ext.load_constants()


@app.get("/")
async def handler(request):
    return text(request.ip)


# Register dependencies
config = Config(database_url="custom://url")
app.ext.dependency(config)
app.ext.dependency(SimpleService())
app.ext.add_dependency(Service, Service.create)
app.ext.add_dependency(Alpha)
app.ext.add_dependency(Beta)
app.ext.add_dependency(Gamma)
app.ext.add_dependency(RequestDependent)
app.ext.add_dependency(CircularA)
app.ext.add_dependency(CircularB)


@app.command
async def simple_inject(svc: SimpleService):
    """Command with simple dependency injection."""
    logger.info(f"SIMPLE_INJECT value={svc.value}")


@app.command
async def inject_with_args(name: str, svc: SimpleService):
    """Command with CLI args and injected dependency."""
    logger.info(f"INJECT_WITH_ARGS name={name} value={svc.value}")


@app.command
async def inject_constructor(svc: Service):
    """Command with custom constructor dependency."""
    logger.info(f"INJECT_CONSTRUCTOR url={svc.config.database_url}")


@app.command
def sync_inject(svc: SimpleService):
    """Sync command with dependency injection."""
    logger.info(f"SYNC_INJECT value={svc.value}")


@app.command
async def nested_inject(beta: Beta):
    """Command with nested dependency."""
    logger.info(f"NESTED_INJECT has_alpha={beta.alpha is not None}")


@app.command(name="custom_name")
async def original_name(svc: SimpleService):
    """Renamed command with dependency injection."""
    logger.info(f"CUSTOM_NAME value={svc.value}")


@app.command
async def optional_request_inject(gamma: Gamma):
    """Command with optional request dependency."""
    logger.info(
        f"OPTIONAL_REQUEST has_beta={gamma.beta is not None} request={gamma.request}"
    )


@app.command
async def request_dep_inject(dep: RequestDependent):
    """Command that should fail because RequestDependent needs Request."""
    logger.info(f"REQUEST_DEP {dep}")


@app.command
async def no_injection(name: str, count: int = 1):
    """Command with no dependencies, just CLI args."""
    logger.info(f"NO_INJECTION name={name} count={count}")


@app.command
async def constant_inject(my_constant: str):
    """Command that injects a config constant."""
    logger.info(f"CONSTANT_INJECT value={my_constant}")


@app.command
async def circular_inject(a: CircularA):
    """Command with circular dependency - should raise error."""
    logger.info(f"CIRCULAR_INJECT {a}")
