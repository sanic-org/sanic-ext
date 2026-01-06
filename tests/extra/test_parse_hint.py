from typing import Any

from sanic_ext.extras.validation.schema import parse_hint


def test_parse_generic_list():
    hint_1 = parse_hint(list[int])
    hint_2 = parse_hint(list[int])

    assert hint_1.origin == hint_2.origin
    assert hint_1.allowed == hint_2.allowed


def test_parse_generic_dict():
    hint_1 = parse_hint(dict[str, Any])
    hint_2 = parse_hint(dict[str, Any])

    assert hint_1.origin == hint_2.origin
    assert hint_1.allowed == hint_2.allowed
