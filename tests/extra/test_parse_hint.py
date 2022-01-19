from typing import Any, Dict, List

import pytest

from sanic_ext.extras.validation.schema import parse_hint


@pytest.mark.parametrize(
    "first,second",
    (
        (List[int], list[int]),
        (Dict[str, Any], dict[str, Any]),
    ),
)
def test_parse_generics(first, second):
    hint_1 = parse_hint(first)
    hint_2 = parse_hint(second)

    assert hint_1.origin == hint_2.origin
    assert hint_1.allowed == hint_2.allowed
