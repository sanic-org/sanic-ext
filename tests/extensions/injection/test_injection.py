from dataclasses import dataclass

import pytest
from sanic import text
from sanic.exceptions import SanicException
from sanic.views import HTTPMethodView
from sanic_ext import Extend


def test_injection_not_allowed_when_ext_disabled(bare_app):
    ext = Extend(bare_app, built_in_extensions=False)

    with pytest.raises(
        SanicException, match="Injection extension not enabled"
    ):
        ext.add_dependency(1, 2)


def test_injection_of_matched_object(app):
    @dataclass
    class Name:
        name: str

    @app.get("/person/<name:str>")
    def handler(request, name: Name):
        request.ctx.name = name
        return text(name.name)

    app.ctx.ext.add_dependency(Name)

    request, response = app.test_client.get("/person/george")

    assert response.body == b"george"
    assert isinstance(request.ctx.name, Name)
    assert request.ctx.name.name == "george"


def test_injection_of_matched_object_as_deprecated_injection(app):
    @dataclass
    class Name:
        name: str

    @app.get("/person/<name:str>")
    def handler(request, name: Name):
        request.ctx.name = name
        return text(name.name)

    message = (
        "The 'ext.injection' method has been deprecated and will be removed "
        "in v22.6. Please use 'ext.add_dependency' instead."
    )
    with pytest.warns(DeprecationWarning, match=message):
        app.ctx.ext.injection(Name)

    request, response = app.test_client.get("/person/george")

    assert response.body == b"george"
    assert isinstance(request.ctx.name, Name)
    assert request.ctx.name.name == "george"


def test_injection_of_simple_object(app):
    @dataclass
    class Person:
        name: str

    @app.get("/person/<name>")
    def handler(request, name: str, person: Person):
        request.ctx.person = person
        return text(person.name)

    app.ctx.ext.add_dependency(Person)

    request, response = app.test_client.get("/person/george")

    assert response.body == b"george"
    assert isinstance(request.ctx.person, Person)
    assert request.ctx.person.name == "george"


def test_injection_of_object_with_constructor(app):
    @dataclass
    class PersonID:
        person_id: int

    @dataclass
    class Person:
        person_id: PersonID
        name: str
        age: int

        @classmethod
        async def create(cls, request, person_id: int):
            return cls(person_id=PersonID(person_id), name="noname", age=111)

    @app.get("/person/<person_id:int>")
    async def person_details(request, person_id: PersonID, person: Person):
        request.ctx.person_id = person_id
        request.ctx.person = person
        return text(
            f"{person.person_id.person_id}\n{person.name}\n{person.age}"
        )

    app.ctx.ext.add_dependency(Person, Person.create)
    app.ctx.ext.add_dependency(PersonID)

    request, response = app.test_client.get("/person/999")

    assert response.body == b"999\nnoname\n111"
    assert isinstance(request.ctx.person_id, PersonID)
    assert isinstance(request.ctx.person, Person)
    assert request.ctx.person.person_id == request.ctx.person_id
    assert request.ctx.person.person_id.person_id == 999
    assert request.ctx.person.name == "noname"
    assert request.ctx.person.age == 111


def test_injection_on_cbv(app):
    @dataclass
    class Name:
        name: str

    class View(HTTPMethodView, attach=app, uri="/person/<name:str>"):
        async def get(self, request, name: Name):
            request.ctx.name = name
            return text(name.name)

        @staticmethod
        async def post(request, name: Name):
            request.ctx.name = name
            return text(name.name)

    app.ctx.ext.add_dependency(Name)

    for client in (app.test_client.get, app.test_client.post):
        request, response = client("/person/george")

        assert response.body == b"george"
        assert isinstance(request.ctx.name, Name)
        assert request.ctx.name.name == "george"
