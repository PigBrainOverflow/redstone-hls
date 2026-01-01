import pyrtl
from .core import Function, Value, Port


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
    max_time = max(time2vals.keys())
    cnter_width = max_time.bit_length()

    pyrtl.reset_working_block()

    # module ports
    go = pyrtl.Input(bitwidth=1, name="go")
    port2wv: dict[Port, pyrtl.WireVector] = {}
    for port in func.ports:
        if port.type.startswith("input"):
            wv = pyrtl.Input(bitwidth=port.width, name=port.name or "")
        else:
            wv = pyrtl.Output(bitwidth=port.width, name=port.name or "")
        port2wv[port] = wv

    cnter = pyrtl.Register(bitwidth=cnter_width, name="cnter")

    # declare internal registers and wires
    # NOTE: some unused registers may be created
    val2ref: dict[Value, tuple[pyrtl.WireVector, pyrtl.Register]] = {}
    for val in bb.body:
        if val.type == "phi":
            # TODO: handle phi nodes
            pass
        elif val.type == "read":
            from_port = val.content["from"]
            from_wv = port2wv[from_port]
            from_reg = pyrtl.Register(bitwidth=from_port.width)
            val2ref[val] = (from_wv, from_reg)
        elif val.type in {"add", "mul"}:
            width = val.content["width"]
            result_wv = pyrtl.WireVector(bitwidth=width)
            result_reg = pyrtl.Register(bitwidth=width)
            val2ref[val] = (result_wv, result_reg)

    # connect logic per time step
    for t, vals in time2vals.items():
        with pyrtl.conditional_assignment:
            with cnter == t if t > 0 else (cnter == 0) & go:
                for val in vals:
                    if val.type == "read":
                        from_wv, from_reg = val2ref[val]
                        from_reg.next |= from_wv
                    elif val.type in {"add", "mul"}:
                        lhs, rhs = val.content["operands"]
                        # use registered value if produced earlier
                        lhs_ref = val2ref[lhs][1] if lhs.content["time"] < t else val2ref[lhs][0]
                        rhs_ref = val2ref[rhs][1] if rhs.content["time"] < t else val2ref[rhs][0]
                        result_wv, result_reg = val2ref[val]
                        if val.type == "add":
                            result_wv <<= lhs_ref + rhs_ref
                        else:  # mul
                            result_wv <<= lhs_ref * rhs_ref
                        result_reg.next |= result_wv
                    elif val.type == "write":
                        value = val.content["value"]
                        to_port = val.content["to"]
                        # use registered value if produced earlier
                        value_ref = val2ref[value][1] if value.content["time"] < t else val2ref[value][0]
                        to_wv = port2wv[to_port]
                        to_wv |= value_ref
                    elif val.type == "emit":
                        to_port = val.content["to"]
                        to_wv = port2wv[to_port]
                        to_wv <<= cnter == t if t > 0 else (cnter == 0) & go

    # counter update
    with pyrtl.conditional_assignment:
        with cnter == 0:
            with go:
                cnter.next |= 1 # start from time 1 because time 0 is handled in this cycle
        with pyrtl.otherwise:
            with cnter >= max_time:
                cnter.next |= 0
            with pyrtl.otherwise:
                cnter.next |= cnter + 1

    return pyrtl.working_block()