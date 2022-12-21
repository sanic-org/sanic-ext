from pathlib import Path

from sanic_ext.extensions.openapi.builders import SpecificationBuilder


def test_specification_singleton():
    spec = SpecificationBuilder()
    spec.tag("foo")

    new_spec = SpecificationBuilder()

    assert spec is new_spec
    assert spec.tags == new_spec.tags


def test_specification_reset(get_docs):
    spec = SpecificationBuilder()

    docs = get_docs()
    assert len(docs["tags"]) == 0

    spec.tag("foo")
    docs = get_docs()
    assert len(docs["tags"]) == 1

    spec.reset()
    docs = get_docs()
    assert len(docs["tags"]) == 0


def test_custom_specification(app):
    petstore_file = Path(__file__).parent / "static" / "petstore.json"
    petstore_data = petstore_file.read_text()
    app.config.OAS_CUSTOM_FILE = petstore_file

    _, response = app.test_client.get("/docs/openapi.json")
    assert response.text == petstore_data
