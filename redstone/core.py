from __future__ import annotations
from typing import Any
from dataclasses import dataclass
import pyrtl


@dataclass(frozen=True)
class Event:
    content: dict[Any, Any]


@dataclass(frozen=True)
class Value:
    type: str
    void: bool
    content: dict[Any, Any]


@dataclass(frozen=True)
class Port:
    name: str | None
    direction: str
    width: int


class BasicBlock:
    _name: str | None
    _guard: Event | None
    _body: list[Value]

    def __init__(self, name: str | None = None, guard: Event | None = None):
        self._name = name
        self._guard = guard
        self._body = []

    def guard(self) -> Event | None:
        return self._guard

    @property
    def body(self) -> list[Value]:
        return self._body

    @body.setter
    def body(self, new_body: list[Value]):
        self._body = new_body

    def __repr__(self) -> str:
        return f"BasicBlock(name={self._name}, guard={self._guard}, body={self._body})"

    @property
    def scheduled(self) -> bool:
        # check if all values in body have a fixed time
        return all(isinstance(val.content.get("time"), int) for val in self._body)

    def schedule(self, objective: str = "ASAP"):
        if objective == "ASAP":
            # TODO
            pass
        else:
            raise NotImplementedError("Unsupported scheduling objective.")

    def to_pyrtl(self) -> pyrtl.Block:
        pass


class Function:
    # function definition
    # or better named "Module" in hardware design
    _name: str | None
    _ports: list[Port]
    _blocks: list[BasicBlock]

    def __init__(self, name: str | None = None):
        self._name = name
        self._ports = []
        self._blocks = []

    @property
    def ports(self) -> list[Port]:
        return self._ports

    @ports.setter
    def ports(self, new_ports: list[Port]):
        self._ports = new_ports

    @property
    def blocks(self) -> list[BasicBlock]:
        return self._blocks

    @blocks.setter
    def blocks(self, new_blocks: list[BasicBlock]):
        self._blocks = new_blocks

    def __repr__(self) -> str:
        repr_str = f"Function(name={self._name}, ports={self._ports}, blocks=[\n"
        for block in self._blocks:
            repr_str += f"  {block},\n"
        repr_str += "])"
        return repr_str


if __name__ == "__main__":
    # build an alu module
    alu = Function(name="alu")

    # define ports
    enable_port = Port(name="enable", direction="input", width=1)
    a_port = Port(name="a", direction="input", width=8)
    b_port = Port(name="b", direction="input", width=8)
    done_port = Port(name="done", direction="output", width=1)
    result_port = Port(name="result", direction="output", width=8)
    alu.ports += [enable_port, a_port, b_port, done_port, result_port]

    # define body
    alu_entry = BasicBlock(name="entry", guard=Event(content={"when": enable_port}))
    alu_entry.body += [
        Value(type="read", void=False, content={"from": a_port, "time": 0}),
        Value(type="read", void=False, content={"from": b_port, "time": 1}),
        Value(type="add", void=False, content={"operands": ["a", "b"]}),
        Value(type="write", void=True, content={"to": result_port, "time": 2}),
        Value(type="emit", void=True, content={"to": done_port, "time": 2})
    ]
    alu._blocks.append(alu_entry)

    print(alu)