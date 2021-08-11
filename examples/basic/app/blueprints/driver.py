from sanic import Blueprint, json

from ..data import test_driver, test_success

bp = Blueprint("Driver", "/driver")


@bp.get("/")
def driver_list(request):
    return json([test_driver])


@bp.get("/<driver_id:int>")
def driver_get(request, driver_id):
    return json(test_driver)


@bp.put("/<driver_id:int>")
def driver_put(request, driver_id):
    return json(test_driver)


@bp.delete("/<driver_id:int>")
def driver_delete(request, driver_id):
    return json(test_success)
