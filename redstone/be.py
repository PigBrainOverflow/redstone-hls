import pyrtl
from .core import Function, BasicBlock, Value, Port


def to_pyrtl(func: Function, is_top: bool = True) -> pyrtl.Block:
    if len(func.blocks) != 1:
        raise NotImplementedError("Only single-block function is supported.")
    bb = func.blocks[0]
    if not bb.scheduled():
        raise RuntimeError("Scheduling required before lowering.")
    if not is_top:
        raise NotImplementedError("Only top-level function is supported.")

    time2vals: dict[int, list[Value]] = {}
    for val in bb.body:
        if val.content["time"] in time2vals:
            time2vals[val.content["time"]].append(val)
        else:
            time2vals[val.content["time"]] = [val]
    cnter_width = max(time2vals.keys()).bit_length()

    pyrtl.reset_working_block()

    # module ports
    rst = pyrtl.Input(bitwidth=1, name="rst")
    port2wv: dict[Port, pyrtl.WireVector] = {}
    for port in func.ports:
        if port.type.startswith("input"):
            wv = pyrtl.Input(bitwidth=port.width, name=port.name or "tmp")
        else:
            wv = pyrtl.Output(bitwidth=port.width, name=port.name or "tmp")
        port2wv[port] = wv

    cnter = pyrtl.Register(bitwidth=cnter_width, name="cnter")
    with pyrtl.conditional_assignment:
        with rst:
            cnter.next |= 0
        with pyrtl.otherwise:
            with cnter == 0:
                pass

    return pyrtl.working_block()