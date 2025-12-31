import pyrtl
from .core import BasicBlock, Value


def to_pyrtl(bb: BasicBlock, is_top: bool = False) -> pyrtl.Block:
    if not bb.scheduled():
        raise RuntimeError("Scheduling required before lowering.")
    time2vals: dict[int, list[Value]] = {}
    for val in bb.body:
        if val.content["time"] in time2vals:
            time2vals[val.content["time"]].append(val)
        else:
            time2vals[val.content["time"]] = [val]
    max_time = max(time2vals.keys())

    pyrtl.reset_working_block()

    active_reg = pyrtl.Register(bitwidth=1, name=f"{bb.name if bb.name else 'tmp'}_active")

    return pyrtl.working_block()