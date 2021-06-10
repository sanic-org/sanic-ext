"""
   isort:skip_file
"""

from collections import defaultdict
from typing import Any, Callable, Dict

from .builders import OperationBuilder, SpecificationBuilder

# Static datastores, which get added to via the oas3.openapi decorators,
# and then read from in the blueprint generation

operations: Dict[Callable[..., Any], OperationBuilder] = defaultdict(
    OperationBuilder
)
specification = SpecificationBuilder()

from .blueprint import blueprint_factory  # noqa


oa3bp = blueprint_factory()
