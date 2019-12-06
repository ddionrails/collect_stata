"""All custom type definitions for the project."""
from typing import Dict, List, TypedDict, Union

Numeric = Union[int, float]


class Categories(TypedDict, total=False):
    """Represent the metadata about categories of a Variable."""

    values: List[Numeric]
    missings: List[bool]
    frequencies: List[Numeric]
    labels: List[str]
    labels_de: List[str]


class Variable(TypedDict, total=False):
    """Represent a single variable extracted from a stata file."""

    study: str
    categories: Categories
    statistics: Dict[str, Numeric]
    dataset: str
    name: str
    label: str
    label_de: str
    scale: str
