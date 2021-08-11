from sanic import Sanic
from sanic.blueprints import Blueprint
from sanic_ext import Extend

from app.blueprints.car import bp as car_blueprint
from app.blueprints.driver import bp as driver_blueprint
from app.blueprints.garage import bp as garage_blueprint
from app.blueprints.manufacturer import bp as manufacturer_blueprint
from app.blueprints.repair import bp as repair_blueprint

app = Sanic("Cars API example")
app.config.API_VERSION = "2.0.0"
app.config.API_TITLE = "Car API"
app.config.API_TERMS_OF_SERVICE = "http://example.org/TOS"
app.config.API_CONTACT_EMAIL = "alice@bob.co"
app.config.API_DESCRIPTION = "Cars API example"
app.config.SERVER_NAME = "http://localhost:9999"

Extend(app)

group = Blueprint.group(
    car_blueprint,
    driver_blueprint,
    garage_blueprint,
    manufacturer_blueprint,
    repair_blueprint,
    version=2,
)

app.blueprint(group)
