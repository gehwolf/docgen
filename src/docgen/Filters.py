import re
from typing import Callable, Literal

EntityType = Literal["function_decl", "struct_decl", "enum_decl", "union_decl", "typedef_decl"]


class FilterRule:
    def __init__(
        self,
        action: Literal["include", "exclude"],
        entity_type: EntityType,
        match_type: Literal["name", "pattern"],
        value: str
    ):
        self.action = action
        self.entity_type = entity_type
        self.match_type = match_type
        self.value = value

        if match_type == "name":
            self.matcher: Callable[[str], bool] = lambda name: name == value
        elif match_type == "pattern":
            pattern = re.compile(value)
            self.matcher = lambda name: bool(pattern.match(name))
        else:
            raise ValueError("match_type must be 'name' or 'pattern'")

    def matches(self, name: str, entity_type: EntityType) -> bool:
        return self.entity_type == entity_type and self.matcher(name)


class DocstringFilter:
    def __init__(self):
        self.rules: list[FilterRule] = []

    def add_rule(self, rule: FilterRule):
        self.rules.append(rule)

    def should_include(self, name: str, entity_type: EntityType) -> bool:
        include_match = False
        exclude_match = False

        for rule in self.rules:
            if rule.matches(name, entity_type):
                if rule.action == "include":
                    include_match = True
                elif rule.action == "exclude":
                    exclude_match = True

        if include_match and not exclude_match:
            return True
        # if not include_match and not exclude_match:
        #     return True  # default to include if no rules apply
        return False
