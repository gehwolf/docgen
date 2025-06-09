from dataclasses import dataclass
from typing import Optional


@dataclass
class DeclarationInfo:
    name: str
    decl_type: str
    is_typedef: bool
    file: str
    line: int
    docstring: Optional[str]
    definition: Optional["DefinitionInfo"] = None  # New field


@dataclass
class DefinitionInfo:
    file: str
    line: int
    is_definition: bool
    docstring: Optional[str]
