import redstone as rs


"""
An adder that adds two 32-bit inputs at G and G + 1 and produces the sum at G + 2,
with an initiation interval (II) of 1.
"""
rs.start_module(name="adder1")

# define ports
a = rs.input(width=32, name="a")
b = rs.input(width=32, name="b")
sum = rs.output(width=32, name="sum")

# define body
# define the main infinite loop, starting from TZERO, i.e., right after global reset
with rs.loop(at=rs.TZERO) as (Tcur, Tnext):
    # Tcur is the start time of current iteration
    # Tnext is the start time of next iteration
    aval, bval, sumval = rs.values((32, 32, 32), names="aval bval sumval")
    rs.at(Tcur).do(rs.NormalAction({"type": "sample", "from": a, "to": aval}))  # read port a at time Tcur
    rs.at(Tcur + 1).do(rs.NormalAction({"type": "sample", "from": b, "to": bval}))  # read port b at time Tcur + 1
    rs.NormalAction({"type": "add", "operands": (aval, bval), "width": 32, "to": sumval})   # we don't need to specify time here, let the compiler figure it out
    rs.at(Tcur + 2).do(rs.NormalAction({"type": "drive", "from": sumval, "to": sum}))   # write port sum at time Tcur + 2

    Tnext.tset(Tcur + 1)    # namely, II = 1

print(rs.current_module())


"""
An adder that adds two 32-bit inputs when enabled, producing the sum two cycles later.
"""
rs.start_module(name="adder2")

# define ports
enable = rs.input_pulse(name="enable")
a = rs.input(width=32, name="a")
b = rs.input(width=32, name="b")
done = rs.output_pulse(name="done")
sum = rs.output(width=32, name="sum")

# define body
with rs.loop(at=rs.TZERO) as (Tcur, Tnext):
    Tenable = rs.wait(rs.PulseEvent(enable), at=Tcur)  # wait for enable pulse starting from Tcur, get the time when the pulse arrives
    aval, bval, sumval = rs.values((32, 32, 32), names="aval bval sumval")  # declare temporary values to hold sampled inputs and computed sum
    rs.at(Tenable).do(
        rs.NormalAction({"type": "sample", "from": a, "to": aval}),
        rs.NormalAction({"type": "sample", "from": b, "to": bval})
    )
    rs.NormalAction({"type": "add", "operands": (aval, bval), "width": 32, "to": sumval})   # we don't need to specify time here, let the compiler figure it out
    rs.at(Tenable + 1).do(
        rs.NormalAction({"type": "drive", "from": sumval, "to": sum}),
        rs.NormalAction({"type": "emit", "pulse": done})
    )

    Tnext.tset(Tenable + 2)    # next iteration starts after current addition is done

print(rs.current_module())


"""
An async branch example: when enabled, if sel == 1, compute multiplication (which takes longer time); else compute addition (which is faster). Finally, output the result and emit done pulse.
"""
rs.start_module(name="async_branch")

# define ports
enable = rs.input_pulse(name="enable")
a = rs.input(width=32, name="a")
b = rs.input(width=32, name="b")
sel = rs.input(width=1, name="sel")
done = rs.output_pulse(name="done")
out = rs.output(width=32, name="out")

# define body
with rs.loop(at=rs.TZERO) as (Tcur, Tnext):
    Tenable = rs.wait(rs.PulseEvent(enable), at=Tcur)  # wait for enable pulse starting from Tcur, get the time when the pulse arrives
    aval, bval, selval, outval = rs.values((32, 32, 1, 32), names="aval bval selval outval")
    rs.at(Tenable).do(
        rs.NormalAction({"type": "sample", "from": a, "to": aval}),
        rs.NormalAction({"type": "sample", "from": b, "to": bval}),
        rs.NormalAction({"type": "sample", "from": sel, "to": selval})
    )
    with rs.branch(condition={"type": "bool", "value": selval}, at=Tenable) as br:
        with br.then(): # multiplication branch, which takes longer time
            rs.within(Tenable, Tenable + 3).do(
                rs.NormalAction({"type": "mul", "operands": (aval, bval), "width": 32, "to": outval})
            )
        with br.otherwise():    # addition branch, can be executed in 1 cycle
            rs.at(Tenable).do(
                rs.NormalAction({"type": "add", "operands": (aval, bval), "width": 32, "to": outval})
            )
    Tjoint = rs.tphi(br)  # get the join point time variable of the branch
    rs.at(Tjoint).do(
        rs.NormalAction({"type": "drive", "from": outval, "to": out}),
        rs.NormalAction({"type": "emit", "pulse": done})
    )

    Tnext.tset(Tjoint + 1) # next iteration starts after the join point plus 1 cycle
    # note that tphi is different from tmax, because tphi is a run-time join point after branches,
    # while tmax is a compile-time maximum of two time variables

print(rs.current_module())