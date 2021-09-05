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
