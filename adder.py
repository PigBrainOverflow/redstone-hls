import redstone as rs


if __name__ == "__main__":
    # build an adder
    adder = rs.Function(name="adder")

    # define ports
    enable_port = rs.Port(name="enable", direction="input", width=1)
    a_port = rs.Port(name="a", direction="input", width=8)
    b_port = rs.Port(name="b", direction="input", width=8)
    done_port = rs.Port(name="done", direction="output", width=1)
    result_port = rs.Port(name="result", direction="output", width=8)
    adder.ports += [enable_port, a_port, b_port, done_port, result_port]

    # define body
    adder_entry = rs.BasicBlock(name="entry", guard=rs.Event(content={"when": enable_port}))
    a_val = rs.Value(type="read", void=False, content={"from": a_port, "time": 0})
    b_val = rs.Value(type="read", void=False, content={"from": b_port, "time": 1})
    sum_val = rs.Value(type="add", void=False, content={"operands": [a_val, b_val]})    # time to be determined by scheduler
    adder_entry.body += [
        a_val, b_val, sum_val,
        rs.Value(type="write", void=True, content={"value": sum_val, "to": result_port, "time": 2}),
        rs.Value(type="emit", void=True, content={"to": done_port, "time": 2})
    ]
    adder._blocks.append(adder_entry)

    # schedule the block
    adder_entry.schedule(objective="ASAP", OutputFlag=0)    # silent mode
    for val in sorted(adder_entry.body, key=lambda v: v.content.get("time", -1)):
        print(f"Value Type: {val.type}, Scheduled Time: {val.content.get('time')}")

    block = rs.to_pyrtl(adder_entry, is_top=True)
    print(block)