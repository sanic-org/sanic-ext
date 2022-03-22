from sys import version_info
from typing import Any, Dict, List

import pytest

from sanic_ext.extras.validation.schema import parse_hint


@pytest.mark.skipif(version_info < (3, 9), reason="Not needed on 3.8")
def test_parse_generic_list():
    hint_1 = parse_hint(List[int])
    hint_2 = parse_hint(list[int])

    assert hint_1.origin == hint_2.origin
    assert hint_1.allowed == hint_2.allowed


@pytest.mark.skipif(version_info < (3, 9), reason="Not needed on 3.8")
def test_parse_generic_dict():
    hint_1 = parse_hint(Dict[str, Any])
    hint_2 = parse_hint(dict[str, Any])

    assert hint_1.origin == hint_2.origin
    assert hint_1.allowed == hint_2.allowed
