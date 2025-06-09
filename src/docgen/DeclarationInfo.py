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
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    is_definition: bool
    docstring: Optional[str]
