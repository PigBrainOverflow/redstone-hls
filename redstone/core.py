from __future__ import annotations
from typing import Any
from dataclasses import dataclass
import gurobipy as grb


@dataclass(eq=False, frozen=True)
class Event:
    content: dict[Any, Any]


@dataclass(eq=False, frozen=True)
class Value:
    type: str
    void: bool
    content: dict[Any, Any]

    @property
    def predecessors(self) -> Any:
        if self.type in {"add", "mul"}:
            return self.content["operands"]
        if self.type in {"write", "store"}:
            return self.content["value"]
        return None


@dataclass(eq=False, frozen=True)
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

    @property
    def name(self) -> str | None:
        return self._name

    @property
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

    def scheduled(self) -> bool:
        # check if all values in body have a fixed time
        return all(isinstance(val.content.get("time"), int) for val in self._body)

    def dependencies(self) -> list[tuple[int, int]]:
        # return list of (producer_index, consumer_index) pairs
        val2idx = {val: idx for idx, val in enumerate(self._body)}
        deps = []
        for idx, val in enumerate(self._body):
            preds = val.predecessors
            try:
                for pred in preds:
                    deps.append((val2idx[pred], idx))
            except TypeError:
                if preds is not None:
                    deps.append((val2idx[preds], idx))
        return deps

    def schedule(self, objective: str = "ASAP", **grb_params):
        # NOTE: phi nodes are always at time 0
        # NOTE: for simplicity, we don't consider resource constraints here
        if objective == "ASAP":
            model = grb.Model("ASAP Scheduling")
            for k, v in grb_params.items():
                model.setParam(k, v)
            deps = self.dependencies()
            n = len(self._body)
            ts = model.addVars(n, vtype=grb.GRB.INTEGER, name="ts") # non-negative integers
            total_time = model.addVar(vtype=grb.GRB.INTEGER, name="total_time")

            model.addConstrs((total_time >= ts[i] for i in range(n)), name="total_time_def")
            for i, val in enumerate(self.body):
                if val.type == "phi":
                    model.addConstr(ts[i] == 0, name=f"phi_node_{i}")
                elif isinstance(val.content.get("time"), int):
                    model.addConstr(ts[i] == val.content["time"], name=f"fixed_time_{i}")
            model.addConstrs((ts[j] - ts[i] >= 0 for i, j in deps), name="deps")

            model.setObjective(total_time, grb.GRB.MINIMIZE)
            model.optimize()
            if model.status == grb.GRB.OPTIMAL:
                for i, val in enumerate(self._body):
                    time_val = int(ts[i].X)
                    val.content["time"] = time_val
            else:
                raise RuntimeError("Scheduling optimization failed.")
        else:
            raise NotImplementedError("Unsupported scheduling objective.")


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
