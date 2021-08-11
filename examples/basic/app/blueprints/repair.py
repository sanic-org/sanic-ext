from sanic import Blueprint, json
from sanic.views import HTTPMethodView

from ..data import test_station

bp = Blueprint("Repair", "/repair")


class RepairStation(HTTPMethodView):
    def get(self, request):
        return json([test_station])

    def post(self, request):
        return json(request.json)


bp.add_route(RepairStation.as_view(), "/station")
