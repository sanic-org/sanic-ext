from sanic import Blueprint, json

from ..data import test_manufacturer, test_success

bp = Blueprint("Manufacturer", "/manufacturer")


@bp.get("/")
def manufacturer_list(request):
    return json([test_manufacturer])


@bp.get("/<manufacturer_id:int>")
def manufacturer_get(request, manufacturer_id):
    return json(test_manufacturer)


@bp.put("/<manufacturer_id:int>")
def manufacturer_put(request, manufacturer_id):
    return json(test_manufacturer)


@bp.delete("/<manufacturer_id:int>")
def manufacturer_delete(request, manufacturer_id):
    return json(test_success)
