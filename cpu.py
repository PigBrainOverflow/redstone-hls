import redstone as rs


"""
A 5-stage CPU example: IF, ID, EX, MEM, WB.
For simplicity, we assume a 4-entry register file and a limited instruction set (ADD, MUL, LOAD, BEQ).
"""

"""
We first define a naive CPU in a sequential manner.
Unfortunately, it cannot be pipelined due to hazards (dependencies).
"""
rs.start_module(name="seq_cpu")

# no ports

# instantiate memories
instr_mem = rs.instantiate({
    "module_name": "Memory1R",
    "width": 32,
    "depth": 256,
    "ports": {
        "raddr": rs.output(width=8, name="instr_mem_raddr"),
        "rdata": rs.input(width=32, name="instr_mem_rdata")
    }
})

data_mem = rs.instantiate({
    "module_name": "Memory1R",  # we don't need write port for this demo
    "width": 32,
    "depth": 256,
    "ports": {
        "raddr": rs.output(width=8, name="data_mem_raddr"),
        "rdata": rs.input(width=32, name="data_mem_rdata")
    }
})

# define states
pc = rs.value(width=8, name="pc")
rf0, rf1, rf2, rf3 = rs.values((32, 32, 32, 32), names="rf0 rf1 rf2 rf3")  # 4-entry register file

# initialize them with zero
rs.at(rs.TZERO).do(
    rs.NormalAction({"type": "drive", "from": 0, "to": pc}),
    rs.NormalAction({"type": "drive", "from": 0, "to": rf0}),
    rs.NormalAction({"type": "drive", "from": 0, "to": rf1}),
    rs.NormalAction({"type": "drive", "from": 0, "to": rf2}),
    rs.NormalAction({"type": "drive", "from": 0, "to": rf3})
)

# define body
with rs.loop(at=rs.TZERO+1) as (Tcur, Tnext):
    # IF stage
    Tif = Tcur
    rs.at(Tif).do(  # feed instruction memory address
        rs.NormalAction({"type": "drive", "from": pc, "to": instr_mem["ports"]["raddr"]})
    )

    # ID stage
    Tid = Tcur + 1
    instr = rs.value(32, name="instr")  # temporary value to hold fetched instruction
    rs.at(Tid).do(  # read instruction memory data
        rs.NormalAction({"type": "sample", "from": instr_mem["ports"]["rdata"], "to": instr})
    )
    # decode instruction fields
    opcode, rd, rs1, rs2, imm = instr[26:32], instr[24:26], instr[22:24], instr[20:22], instr[0:20]
    # read register file based on decoded fields
    rsv1, rsv2 = rs.values((32, 32), names="rsv1 rsv2")

    with rs.switch(selector=rs1) as sw:
        with sw.case(0):
            rs.NormalAction({"type": "drive", "from": rf0, "to": rsv1})
        with sw.case(1):
            rs.NormalAction({"type": "drive", "from": rf1, "to": rsv1})
        with sw.case(2):
            rs.NormalAction({"type": "drive", "from": rf2, "to": rsv1})
        with sw.default():  # rs1 == 3
            rs.NormalAction({"type": "drive", "from": rf3, "to": rsv1})

    with rs.switch(selector=rs2) as sw:
        with sw.case(0):
            rs.NormalAction({"type": "drive", "from": rf0, "to": rsv2})
        with sw.case(1):
            rs.NormalAction({"type": "drive", "from": rf1, "to": rsv2})
        with sw.case(2):
            rs.NormalAction({"type": "drive", "from": rf2, "to": rsv2})
        with sw.default():  # rs2 == 3
            rs.NormalAction({"type": "drive", "from": rf3, "to": rsv2})

    # EX + MEM stages
    Tex, Tmem = Tcur + 2, Tcur + 3
    res = rs.value(32, name="res")  # temporary value to hold execution result
    with rs.switch(selector=opcode, at=Tex) as sw:
        with sw.case(0):    # ADD
            rs.NormalAction({"type": "add", "operands": (rsv1, rsv2), "width": 32, "to": res})
            rs.NormalAction({"type": "add", "operands": (pc, 4), "to": pc})  # increment PC
        with sw.case(1):    # MUL
            rs.NormalAction({"type": "mul", "operands": (rsv1, rsv2), "width": 32, "to": res})
            rs.NormalAction({"type": "add", "operands": (pc, 4), "to": pc})  # increment PC
        with sw.case(2):    # LOAD
            rs.NormalAction({"type": "drive", "from": rsv1, "to": data_mem["ports"]["raddr"]})
            rs.at(Tmem).do(  # read data memory data
                rs.NormalAction({"type": "sample", "from": data_mem["ports"]["rdata"], "to": res})
            )
            rs.NormalAction({"type": "add", "operands": (pc, 4), "to": pc})  # increment PC
        with sw.default():  # BEQ
            rs.NormalAction({"type": "bool_eq", "operands": (rsv1, rsv2), "to": res})
            with rs.branch(condition={"type": "bool", "value": res}) as br:
                with br.then():
                    rs.NormalAction({"type": "add", "operands": (pc, imm), "to": pc})  # branch taken
                with br.otherwise():
                    rs.NormalAction({"type": "add", "operands": (pc, 4), "to": pc})  # branch not taken

    # WB stage
    Twb = Tcur + 4
    with rs.branch(condition={"type": "bool", "value": opcode != 3}, at=Twb) as br:  # no write back for BEQ
        with br.then():
            with rs.switch(selector=rd, at=Twb) as sw:
                with sw.case(0):
                    rs.NormalAction({"type": "drive", "from": res, "to": rf0})
                with sw.case(1):
                    rs.NormalAction({"type": "drive", "from": res, "to": rf1})
                with sw.case(2):
                    rs.NormalAction({"type": "drive", "from": res, "to": rf2})
                with sw.default():  # rd == 3
                    rs.NormalAction({"type": "drive", "from": res, "to": rf3})

    Tnext.tset(Tcur + 1)    # it fails!

print(rs.current_module())


"""

"""