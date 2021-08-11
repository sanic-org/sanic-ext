import datetime

from .models import Car, Garage, Manufacturer, Person, Station, Status

test_manufacturer = Manufacturer(
    uid=1,
    name="Nissan",
    start_date=datetime.date(year=1933, month=12, day=26),
)

test_driver = Person(
    uid=2,
    name="Alice",
    birthday=datetime.date(year=2010, month=3, day=31),
)

test_passenger = Person(
    uid=3,
    name="Bob",
    birthday=datetime.date(year=2010, month=3, day=31),
)

test_car = Car(
    uid=3,
    on=False,
    doors=2,
    color="black",
    make=test_manufacturer,
    driver=test_driver,
    passengers=[test_passenger],
)

test_garage = Garage(uid=4, spaces=2, cars=[test_car])

test_success = Status(success=True)

test_station = Station(
    uid=5,
    phone_number="1234567890",
    location="Seattle",
)
