from sanic import Blueprint, Request, Sanic
from sanic.response import json
from sanic.worker.inspector import Inspector


def setup_health_endpoint(app: Sanic) -> None:
    bp = Blueprint("SanicHealth", url_prefix=app.config.HEALTH_URL_PREFIX)

    @bp.get(app.config.HEALTH_URI_TO_INFO)
    async def info(request: Request):
        return json(Inspector._make_safe(dict(request.app.m.workers)))

    app.blueprint(bp)
