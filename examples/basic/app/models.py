from dataclasses import dataclass
from datetime import date
from typing import List


@dataclass
class Manufacturer:
    uid: int
    name: str
    start_date: date


@dataclass
class Person:
    uid: int
    name: str
    birthday: date


@dataclass
class Car:
    uid: int
    on: bool
    doors: int
    color: str
    make: Manufacturer
    driver: Person
    passengers: List[Person]


@dataclass
class Garage:
    uid: int
    spaces: int
    cars: List[Car]


@dataclass
class Status:
    success: bool


@dataclass
class Station:
    uid: int
    location: str
    phone_number: str
