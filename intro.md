## Overview
We designed a hardware description language (HDL) that allows seamless integration of high-level imperative programming constructs with low-level hardware timing semantics.

## Example
A dynamic length dot product module can take two inputs of varying lengths and compute their dot product.

```
module dyn_dot_product(
    enable: rs.pulse,
    n: rs.input[5],
    a: rs.input[32],
    b: rs.input[32],
    done: rs.pulse,
    res: rs.output[64]
) [forever] {   # forever is a shorthand for "while (true) {body}"
    let G = await enable;   # wait for enable pulse, return the timestamp
    let n = n@G;    # read n at timestamp G
    let mut i = 0;
    let mut res = 0;
    while (i < n) {
        let a_i = a@(G + 2*i + 1);   # read a[i] at timestamp G + i + 1
        let b_i = b@(G + 2*i + 1);   # read b[i] at timestamp G + i + 1
        res = res + (a_i * b_i);
        i = i + 1;
    } @ T
    while (i < n) {
        T = await enable;
        let a_i = a@(T + i + 1);   # read a[i] at timestamp T + i + 1
        let b_i = b@(T + i + 1);   # read b[i] at timestamp T + i + 1
        res = res + (a_i * b_i);
        i = i + 1;
    }
    let H = emit done;
    res@H = res;   # write result at timestamp H
}
```

```
module dyn_dot_product_ddr<DDR>(
    enable: rs.pulse,
    n: rs.input[5],
    a_base: rs.input[32],
    b_base: rs.input[32],
    done: rs.pulse,
    res: rs.output[64]
) {
    inst ddr_reader = DDR::reader(); # instantiate DDR reader
    let G = await enable;
    let n = n@G;
    let a_base = a_base@G;
    let b_base = b_base@G;
    let mut i = 0;
    let mut res = 0;
    while (i < n) {
        let H = emit ddr_reader.enable; # call it for a[i]
        ddr_reader.raddr@H = a_base + i;    # assume word-addressable
        let I = await ddr_reader.done;  # wait for DDR read to complete
        let a_i = ddr_reader.rdata@I;   # read a[i]
        emit ddr_reader.enable@I;   # call it again for b[i]
        ddr_reader.raddr@I = b_base + i;
        let J = await ddr_reader.done;
        let b_i = ddr_reader.rdata@J;   # read b[i]
        res = res + (a_i * b_i);
        i = i + 1;
    }
    let K = emit done;
    res@K = res;
}
```

Note that `G = await enable` is just a shorthand for `while (!enable) @G` and `Pulse` ports output `0` by default unless emitted.

```
module simple_alu(
    enable: rs.InputPulse,
    op: rs.Input[2],    // 00: ADD, 01: MUL, 10: FP.DIV
    a: rs.Input[32],
    b: rs.Input[32],
    done: rs.OutputPulse,
    res: rs.Output[32]
) [forever] {   // forever is a shorthand for "while (true) {body}"
    // instantiate a floating-point divider
    inst fp_div = FP_DIV();

    // wait for enable pulse
    await enable@G;

    // read inputs at timestamp G
    let op = op@G;
    let a = a@G;
    let b = b@G;

    if (op[1] == 0) {   // ADD or MUL
        let result = (op[0] == 0) ? (a + b) : (a * b);
    }
    else {  // FP.DIV
        emit fp_div.enable@G;   // call the divider
        fp_div.a@G = a;
        fp_div.b@G = b;
        await fp_div.done@H assume H >= G;   // wait for division to complete
        let result = fp_div.res@H;
    }

    // emit done pulse and write result
    emit done@I;
    res@I = result;
}
```



```
// RISC-V 5-stage CPU
Entry:  // when the cpu is reset
    (empty)

Forever: [II = 1]    // timeline anotation
    // static instances
    imem = Memory();    // assume synchronous memory
    dmem = Memory();

    // header
    %pc = phi({Entry: 0, Fetch: %pc_next});
    %r0 = phi({Entry: 0, Writeback: %r0_next});
    %r1 = phi({Entry: 0, Writeback: %r1_next});
    %r2 = phi({Entry: 0, Writeback: %r2_next});
    %r3 = phi({Entry: 0, Writeback: %r3_next}); // for simplicity, only 4 registers

    // IF stage @G
    write imem.raddr = %pc;

    // DE stage @G+1
    %instr = read imem.rdata;
    %opcode = %instr[1:0];  // for simplicity, only 4 instructions
    %rs1 = %instr[3:2];
    %rs2 = %instr[5:4];
    %rd = %instr[7:6];
    %imm = %instr[15:8];
    if %rs == 0: (empty)
    else if %rs == 1: (empty)
    else if %rs == 2: (empty)
    else: (empty)
    %rs1_val = phi({%rs == 0: %r0, %rs == 1: %r1, %rs == 2: %r2, else: %r3});
    // same for %rs2_val

    // EX stage @G+2
    if %opcode == 0:   // ADD
        %alu_result = %rs1_val + %rs2_val;
    else if %opcode == 1:  // SUB
        %alu_result = %rs1_val - %rs2_val;
    else if %opcode == 2:  // LOAD
        %alu_result = %rs1_val + %imm;
    else if %opcode == 3:  // STORE
        %alu_result = %rs1_val + %imm;
    %alu_result = phi({%opcode == 0: %alu_result, %opcode == 1: %alu_result, %opcode == 2: %alu_result, else: %alu_result});

    // MEM stage @G+3
    if %opcode == 2:   // LOAD
        write dmem.raddr = %alu_result;
        emit dmem.renable;
    else if %opcode == 3:  // STORE
        write dmem.waddr = %alu_result;
        emit dmem.wenable;

    // WB stage @G+4
    if %opcode == 0 or %opcode == 1:   // ADD or SUB
        %rd_val = %alu_result;
    else if %opcode == 2:  // LOAD
        %rd_val = read dmem.rdata;

    // update pc and registers
    %pc_next = %pc + 4;
    %r0_next = phi({%rd == 0: %rd_val, else: %r0});
    %r1_next = phi({%rd == 1: %rd_val, else: %r1});
    %r2_next = phi({%rd == 2: %rd_val, else: %r2});
    %r3_next = phi({%rd == 3: %rd_val, else: %r3});
```