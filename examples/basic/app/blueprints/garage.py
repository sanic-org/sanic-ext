from sanic import Blueprint, json

from ..data import test_garage, test_success

bp = Blueprint("Garage", "/garage")


@bp.get("/")
async def get_garage(request):
    return json(test_garage)


@bp.get("/cars")
async def get_cars(request):
    return json(test_garage.get("cars"))


@bp.put("/car")
async def add_car(request):
    return json(test_success)
