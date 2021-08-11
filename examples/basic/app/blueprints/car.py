from sanic import Blueprint, json

from ..data import test_car, test_success

bp = Blueprint("Car", "/car")


@bp.get("/")
def car_list(request):
    return json([test_car])


@bp.get("/<car_id:int>")
def car_get(request, car_id):
    return json(test_car)


@bp.put("/<car_id:int>")
def car_put(request, car_id):
    return json(test_car)


@bp.delete("/<car_id:int>")
def car_delete(request, car_id):
    return json(test_success)
