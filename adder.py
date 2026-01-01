import redstone as rs
import pyrtl


if __name__ == "__main__":
    # Timeline:
    # time G: await enable; read a
    # time G+1: read b
    # time G+2: write a+b to result; emit done

    # build an adder
    adder = rs.Function(name="adder")

    # define ports
    a_port = rs.Port(name="a", type="inputbus", width=32)
    b_port = rs.Port(name="b", type="inputbus", width=32)
    done_port = rs.Port(name="done", type="outputpulse", width=1)
    result_port = rs.Port(name="result", type="outputbus", width=32)
    adder.ports += [a_port, b_port, done_port, result_port]

    # define body
    adder_entry = rs.BasicBlock(name="entry")
    a_val = rs.Value(type="read", void=False, content={"from": a_port, "time": 0})
    b_val = rs.Value(type="read", void=False, content={"from": b_port, "time": 1})
    sum_val = rs.Value(type="add", void=False, content={"width": 32, "operands": [a_val, b_val]})    # time to be determined by scheduler
    adder_entry.body += [
        a_val, b_val, sum_val,
        rs.Value(type="write", void=True, content={"value": sum_val, "to": result_port, "time": 2}),
        rs.Value(type="emit", void=True, content={"to": done_port, "time": 2})
    ]
    adder._blocks.append(adder_entry)

    # schedule the block
    adder_entry.schedule(objective="ASAP", OutputFlag=0)    # silent mode
    # for val in sorted(adder_entry.body, key=lambda v: v.content.get("time", -1)):
    #     print(f"Value Type: {val.type}, Scheduled Time: {val.content.get('time')}")

    # lower to pyrtl
    block = rs.to_pyrtl(adder, is_top=True)
    with open("adder.v", "w") as f:
        pyrtl.output_to_verilog(f, add_reset=True, block=block)

    # simulate
    sim = pyrtl.Simulation()

    def inspect_all():
        print("go = ", sim.inspect("go"))
        print("a = ", sim.inspect("a"))
        print("b = ", sim.inspect("b"))
        print("result = ", sim.inspect("result"))
        print("done = ", sim.inspect("done"))
        print("cnter = ", sim.inspect("cnter"))
        print("active = ", sim.inspect("active"))
        print("-----")

    inspect_all()
    sim.step({"go": 1, "a": 10, "b": 9999})
    inspect_all()
    sim.step({"go": 0, "a": 9999, "b": 20})
    inspect_all()
    sim.step({"go": 0, "a": 0, "b": 0})
    inspect_all()
    sim.step({"go": 0, "a": 0, "b": 0})
    inspect_all()