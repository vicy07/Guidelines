from __future__ import annotations

from typing import Callable, Protocol, TypeAlias


class Scanner(Protocol):
    def run(self, action: str, args: list[str]) -> dict:
        ...


ArgResolver: TypeAlias = Callable[[list[str]], list[str]]
AllPlanStep: TypeAlias = tuple[str, str, ArgResolver]
