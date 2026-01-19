from __future__ import annotations
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any


class Module:
    name: str
    ports: list[dict[str, Any]]
    instances: list[dict[str, Any]]
    top_region: Region
    _current_region: Region

    def __init__(self, name: str):
        self.name = name
        self.ports = []
        self.instances = []
        self.top_region = Region()
        self._current_region = self.top_region  # initialize current region to top region

    def __repr__(self) -> str:
        return f"Module(name={self.name}, ports={self.ports}, instances={self.instances}, top_region={self.top_region})"

    def current_region(self) -> Region:
        return self._current_region


_working_module: Module | None = None

def start_module(name: str = "top"):
    """
    Start a new working module.
    """
    global _working_module
    _working_module = Module(name)

def current_module() -> Module:
    """
    Return the current working module.
    """
    global _working_module
    if _working_module is None:
        raise RuntimeError("No working module. Please call start_module() first.")
    return _working_module


"""
Ports
"""
def input(width: int, name: str | None = None) -> dict[str, Any]:
    port = {"type": "bus", "direction": "input", "width": width, "name": name}
    current_module().ports.append(port)
    return port

def input_pulse(name: str | None = None) -> dict[str, Any]:
    port = {"type": "pulse", "direction": "input", "name": name}
    current_module().ports.append(port)
    return port

def output(width: int, name: str | None = None) -> dict[str, Any]:
    port = {"type": "bus", "direction": "output", "width": width, "name": name}
    current_module().ports.append(port)
    return port

def output_pulse(name: str | None = None) -> dict[str, Any]:
    port = {"type": "pulse", "direction": "output", "name": name}
    current_module().ports.append(port)
    return port


class TVar:
    """
    Represents a time variable.
    """
    def __add__(self, delay: int) -> TVar:
        return TVar()   # TODO: implement it

    @staticmethod
    def tmax(a: TVar, b: TVar) -> TVar:
        return TVar()   # TODO: implement it

    def tset(self, other: TVar):
        """
        Force this TVar to be equal to another TVar.
        """
        pass    # TODO: implement it

    def tbefore(self, other: TVar):
        """
        Force this TVar to be before another TVar.
        """
        pass    # TODO: implement it

    def tafter(self, other: TVar):
        """
        Force this TVar to be after another TVar.
        """
        pass    # TODO: implement it

TZERO = TVar()  # time variable representing time 0, which means the start of everything, e.g., after reset


class Action:
    """
    Represents an action, which can be associated with a time variable or within a time range.
    An action can be a normal action or a control flow action.
    """
    pass


class LoopAction(Action):
    """
    Represents a loop action.
    """
    iter_start: TVar
    next_iter_start: TVar
    body: Region

    def __repr__(self) -> str:
        return f"LoopAction(iter_start={self.iter_start}, next_iter_start={self.next_iter_start}, body={self.body})"


class BranchAction(Action):
    """
    Represents a branch action.
    """
    condition: dict[str, Any]
    true_region: Region
    false_region: Region

    def __init__(self, condition: dict[str, Any], true_region: Region, false_region: Region):
        self.condition = condition
        self.true_region = true_region
        self.false_region = false_region


    def __repr__(self) -> str:
        return f"BranchAction(condition={self.condition}, true_region={self.true_region}, false_region={self.false_region})"


class NormalAction(Action):
    content: dict[str, Any]

    def __init__(self, content: dict[str, Any] | None = None):
        if content is None:
            content = {}
        self.content = content

    def __repr__(self) -> str:
        return f"NormalAction(content={self.content})"


@contextmanager
def loop(at: TVar | None = None):
    """
    Context manager for defining a loop.
    """
    module = current_module()
    current_region = module.current_region()
    iter_start = TVar()
    next_iter_start = TVar()
    loop_body = Region()
    loop_action = LoopAction()
    loop_action.iter_start = iter_start
    loop_action.next_iter_start = next_iter_start
    loop_action.body = loop_body
    current_region.actions.append(loop_action)
    previous_region = module._current_region
    module._current_region = loop_body
    try:
        yield iter_start, next_iter_start
    finally:
        module._current_region = previous_region


class BranchContext:
    module: Module
    prev_region: Region
    action: BranchAction

    def __init__(self, module: Module, prev_region: Region, action: BranchAction):
        self.module = module
        self.prev_region = prev_region
        self.action = action

    @contextmanager
    def then(self):
        self.module._current_region = self.action.true_region
        try:
            yield
        finally:
            self.module._current_region = self.prev_region

    @contextmanager
    def otherwise(self):
        self.module._current_region = self.action.false_region
        try:
            yield
        finally:
            self.module._current_region = self.prev_region


def tphi(branch_ctx: BranchContext) -> TVar:
    """
    Return the time variable representing the join point of the branch.
    """
    return TVar()   # TODO: implement it


@contextmanager
def branch(*, condition: dict[str, Any], at: TVar | None = None):
    """
    Usage:
      with branch(condition=cond) as b:
          with b.then():
              ...
          with b.otherwise():
              ...
    """
    m = current_module()
    parent = m.current_region()

    true_r = Region()
    false_r = Region()

    act = BranchAction(condition=condition, true_region=true_r, false_region=false_r)
    parent.actions.append(act)

    ctx = BranchContext(module=m, prev_region=parent, action=act)

    # keep parent as current while user selects then/else
    prev = m._current_region
    m._current_region = parent
    try:
        yield ctx
    finally:
        m._current_region = prev


class Value:
    """
    Represents an intermediate value.
    """
    name: str | None
    width: int

    def __init__(self, width: int, name: str | None = None):
        self.width = width
        self.name = name

    def __repr__(self) -> str:
        return f"Value(name={self.name}, width={self.width})"

    def __getitem__(self, key: slice | int) -> Value:
        return Value(width=self.width, name=self.name)  # TODO: implement slicing


def value(width: int, name: str | None = None) -> Value:
    val = Value(width, name)
    # add val to current region
    current_module().current_region().values.append(val)
    return val

def values(widths: tuple[int, ...], names: str | None = None) -> tuple[Value, ...]:
    vals = tuple(Value(width, name) for width, name in zip(widths, names.split() if names else ()))
    # add vals to current region
    current_module().current_region().values.extend(vals)
    return vals


class Region:
    """
    Represents a group of time variables and actions.
    """
    name: str | None
    tvars: list[TVar]
    values: list[Value]
    actions: list[Action]

    def __init__(self, name: str | None = None):
        self.name = name
        self.tvars = []
        self.values = []
        self.actions = []

    def __repr__(self) -> str:
        return f"Region(name={self.name}, tvars={self.tvars}, values={self.values}, actions={self.actions})"


class At:
    tvar: TVar

    def __init__(self, tvar: TVar):
        self.tvar = tvar

    def do(self, *actions: Action):
        region = current_module().current_region()
        for action in actions:
            region.actions.append(action)


def at(tvar: TVar) -> At:
    return At(tvar)


class Within:
    trange: tuple[TVar | None, TVar | None]

    def __init__(self, trange: tuple[TVar | None, TVar | None]):
        self.trange = trange

    def do(self, actions: tuple[Action, ...] | Action):
        pass


def within(tlower: TVar | None = None, tupper: TVar | None = None) -> Within:
    return Within((tlower, tupper))


class Event:
    """
    Represents an event that can be waited on.
    """
    pass


class PulseEvent(Event):
    pulse: dict[str, Any]

    def __init__(self, pulse: dict[str, Any]):
        self.pulse = pulse

    def __repr__(self) -> str:
        return f"PulseEvent(pulse={self.pulse})"


def wait(event: Event, at: TVar) -> TVar:
    """
    Wait for an event starting from a given time variable.
    Return a time variable indicating when the event is triggered.
    """
    return TVar()   # TODO: implement it


def instantiate(info: dict[str, Any]) -> dict[str, Any]:
    """
    Instantiate a module or primitive.
    """
    current_module().instances.append(info)
    return info


@dataclass
class SwitchAction(Action):
    selector: Value
    cases: dict[Any, Region] = field(default_factory=dict)
    default_region: Region | None = None

    def __repr__(self) -> str:
        return f"SwitchAction(selector={self.selector}, cases={list(self.cases.keys())}, default_region={self.default_region})"


# add near BranchContext

class SwitchContext:
    module: Module
    prev_region: Region
    action: SwitchAction

    def __init__(self, module: Module, prev_region: Region, action: SwitchAction):
        self.module = module
        self.prev_region = prev_region
        self.action = action

    @contextmanager
    def case(self, value: Any):
        r = self.action.cases.get(value)
        if r is None:
            r = Region()
            self.action.cases[value] = r
        self.module._current_region = r
        try:
            yield
        finally:
            self.module._current_region = self.prev_region

    @contextmanager
    def default(self):
        if self.action.default_region is None:
            self.action.default_region = Region()
        self.module._current_region = self.action.default_region
        try:
            yield
        finally:
            self.module._current_region = self.prev_region


# add near branch()

@contextmanager
def switch(*, selector: Value, at: TVar | None = None):
    """
    Usage:
      with switch(selector=sel) as s:
          with s.case(0):
              ...
          with s.case(1):
              ...
          with s.default():
              ...
    """
    m = current_module()
    parent = m.current_region()

    act = SwitchAction(selector=selector)
    parent.actions.append(act)

    ctx = SwitchContext(module=m, prev_region=parent, action=act)

    prev = m._current_region
    m._current_region = parent
    try:
        yield ctx
    finally:
        m._current_region = prev
