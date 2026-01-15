# Before Everything
If we think Verilog as assembly language, current HLS in C/C++ is definitely not the real C parallel product to Verilog. The main problem is the semantic gap between HLS and Verilog is too large. HLS tries to abstract away too many hardware details, making it difficult to predict the generated hardware behavior. Considering C language in software domain, it is also low-level enough to express machine behavior (e.g., pointer arithmetic, bit manipulation) but with structured programming constructs (e.g., loops, functions) while still providing good interface to compose with low-level assembly code. Filament project tried to be a Rust parallel to Verilog. The success of Rust in software domain is mainly due to the phonomenon that more than 70% of bugs are memory-related (https://www.chromium.org/Home/chromium-security/memory-safety/, https://www.cs.purdue.edu/homes/lintan/publications/bugchar-emse14.pdf), and Rust's ownership system can eliminate most of them at compile time. It solves the real pain points in software development. However, there's no clear evidence that pipelining safety is such a large problem that needs to be solved at the cost of expressiveness and ease of use. OpenSPARC T1 RTL bug study (296 bugs, LSU+TLU): LSU: 59% logic (wrong combinational/control), 35% algorithmic/spec, 6% RTL timing/latency (wrong cycle/FF placement). TLU: 49% logic, 47% algorithmic/spec, 4% RTL timing/latency. (https://people.inf.ethz.ch/omutlu/pub/hwbugs_micro08.pdf). It shows that only a small portion of bugs are related to timing/latency, while most bugs are logic or spec related, which suggests that an HDL that allows better control flow construction together with a user-specified timeline behavior may be more beneficial.

It allows:
   - Timeline notation;
   - Unsafe composition with low-level blocks;
   - Automatic scheduling for high-level blocks;
   - Control-dataflow separation.


The goal is to 1) unify HLS and RTL, the whole lang is still an HDL since users are still designing hardware modules and have low-level control over hardware (can write verilog-like code); on the other side, we pick the most valuable features from HLS: scheduling inference and structured programming constructs; 2) unify latency-insensitive and latency-sensitive designs, by allowing timeline as a first-class object and timeline algebra (an extension of tropical algebra); 3) provide a general-purpose HDL which is suitable for both control-intensive and compute-intensive designs. Unlike Filament and its successors, we emphasize more on expressiveness and easy to write, rather than safety. The only guarantee is that the timeline annotations are respected, if cannot, compiler will raise infeasible error. However, the corresponding ir we propose is highly principled and allows future research on program analysis and verification, e.g., bringing Filament (time-sensitive interface) and Wire Sorts (time-insensitive).

# Overview
For clearness, we use a python-like pseudocode to illustrate the language features. The actual syntax can be designed later. In most places, we omit time variable declarations for brevity.

```python
def dyn_dot_product(
    enable: rs.InputPulse,
    n: rs.Input[32],
    a: rs.Input[32],
    b: rs.Input[32],
    done: rs.OutputPulse,
    res: rs.Output[64]
) [forever] {   # forever is a shorthand for "while (true) {func-body}"
    # await is a shorthand for "while (!condition) {}"
    await enable @G;
    n_val = read n @G;    # read port n at timestamp G
    for (i = 0, H = G + 1; i < n_val; i = i + 1, H = H + 1) {   # II = 1 pipeline
        a_i = read a @H;   # read a[i] at timestamp H
        b_i = read b @H;   # read b[i] at timestamp H
        acc = acc + (a_i * b_i);    # don't specify timestamp for acc, compiler will schedule it
    }
    emit done @I;   # don't care whether I equals G + 1 + n_val or not, just make sure done is emitted after the loop
    write res = acc @I; # and res is written at the same cycle as done
}
```

The whole language is still hardware module oriented, except that you express the desired behavior in a high-level structured manner. It is sequential, without any parallel construct. Parallelism is inferred by compiler based on timeline annotations and dependencies. The timeline annotation is optional, so you can leave it blank for high-level blocks and let compiler handle everything. `Input[W]` and `Output[W]` are W-bit wide data ports, the semantics of a `Output[W]` is that unless written to at specified timestamp, its value is DC (don't care), which leaves optimization space for the compiler. `OutputPulse` is a single-bit output port that is only high for one cycle when emitted, otherwise low. It also can be used just like `Output[1]`.

```python
def async_branch(
    enable: rs.InputPulse,
    sel: rs.Input[1],
    done: rs.OutputPulse,
    out: rs.Output[32]
) [forever] {
    await enable @G;
    sel_val = read sel @G;
    Time H; # declare a new timeline variable H
    if (sel_val == 0) {
        # do something very fast
        ...
        ... @I;
        H = I + 1; # set H to I + 1
    }
    else {
        # do something slow
        ...
        ... @J;
        H = J + 1;
    }
    emit done @H;
    write out = ... @H;
}
```

In this example, we show how to deal with variable-latency control flow with timeline variables. Here H is a timeline variable that can be assigned to different timestamps based on the branch taken. It will be lowered to our timeline-ir. In order to represent timeline assignment precisely, we introduce `timeline phi nodes`. In this case, `%H = phi(if_block: %I + 1, else_block: %J + 1)`. Unlike SSA phi nodes, which mostly don't have a concrete lowered representation, timeline phi nodes typically need to be materialized into a counter that resets when one of the branches' done signal is received.

```python
def sync_branch(
    enable: rs.InputPulse,
    sel: rs.Input[1],
    done: rs.OutputPulse,
    out: rs.Output[32]
) [forever] {
    await enable @G;
    sel_val = read sel @G;
    Time H;
    if (sel_val == 0) {
        # do something
        ...
        ... @H;
    }
    else {
        # do something else
        ...
        ... @H;
    }
    emit done @H;
    write out = ... @H;
}
```

This time, we force both branches to finish at the same time H, though we don't care what H is. The compiler will try to schedule both branches to finish at the same time, and by default, as soon as possible.

```python
def static_branch(
    enable: rs.InputPulse,
    sel: rs.Input[1],
    out: rs.Output[32]
) [forever] {
    await enable @G;
    sel_val = read sel @G;
    if (sel_val == 0) {
        # do something
        ...
        ... @(G + 4);
    }
    else {
        # do something else
        ...
        ... @(G + 4);
    }
    write out = ... @(G + 4);
}
```

In this example, we force both branches to finish at a specific time G + 4. There's no need for done port since the latency is specified by the designer already.

```python
def par_dispatch(
    enable: rs.InputPulse,
    done: rs.OutputPulse
) [forever] {
    instance worker1 = WorkerModule::new();
    instance worker2 = WorkerModule::new();
    await enable @G;
    # launch two tasks in parallel
    emit worker1.enable @G; # trigger
    write worker1.data = ... @G;    # and feed data
    emit worker2.enable @G;
    write worker2.data = ... @G;

    # maybe do other things here

    # wait for both to finish
    await worker1.done @H1;
    await worker2.done @H2;
    H = max(H1, H2); # H is the later one, this is the same as saying join(worker1, worker2) @H

    emit done @H;
}
```

# Design Choices
`await` is a blocking operation that stalls the current function until the condition is met at the specified timestamp. Unlike other channel-based HDLs and HLS, e.g., XLS, we don't implicitly create a single-producer single-consumer FIFO channel for communication between blocks. Instead, FIFO is a standard library component that can be instantiated and used explicitly. This design makes our HDL more general and providing finer control to the designer, e.g., FIFO depth.

There's no concept of "function call" in this language. It can be expressed by emit enable, feed data, await done pattern as shown in the examples.

There's no concept of par/seq block since they can be expressed by timeline annotations with `before`/`after` constraints. For example, a par block can be expressed by launching multiple tasks at the same timestamp and joining them later. A seq block can be expressed by launching tasks one after another with proper timeline annotations.

# Evaluation Plan
As a general-purpose HDL, we can evaluate it by two kinds of designs.

## Control-intensive designs, e.g., RISC-V 5-stage CPU
This is not isacomp (though it can be target code for isacomp) so designers still need to specify behaviors like stall/speculative execution. But with timeline annotations, it should be easier to express and if there's no hazard, the design should be pipelined automatically by saying `G = G + 1` in the main loop. For brevity, we only consider a CPU with a 2-entry register file and a simple instruction set including add and mul only. Therefore, there's no branch and memory access in this example. We just reduce it to a 4-stage pipeline (fetch, decode, execute, writeback).

```python
def simple_cpu(
    imem_addr: rs.Output[32],
    imem_data: rs.Input[32]
) [forever(G = G + 1)] {
    # instruction fetch
    write imem_addr = pc @G;

    # instruction decode
    instr = read imem_data @(G + 1);
    opcode = instr[6:0];
    rs1 = instr[19:15];
    rs2 = instr[24:20];
    rd = instr[11:7];
    imm = sign_extend(instr[31:20]);

    # execute
    rs1_val = 
    rs2_val = 
    if (opcode == 
}
```

## Compute-intensive designs


# Tutorial Examples

## Pipelined DDR Read + DSP Compute with Double Buffering
In this section, we show how to design a pipelined data processing module with double buffering and burst read from DDR. The module reads data from DDR in batches of 256 elements, feeds them parallelly to 2 DSPs to do computation, and outputs the results in a streaming manner. When the module is enabled, it immediately reads `base_addr` and `len` from input ports, then fetch data from DDR in bursts of 256 elements. Before the output stream is valid, it emits `batch_done` pulse.

We first define the interface of this module:
```python
def ddr_read_compute(
    enable: InputPulse,
    base_addr: Input[32],
    n: Input[32],
    batch_done: OutputPulse,
    res0: Output[64],
    res1: Output[64]
) forever
```
Pulse ports are single-bit ports that are only high for one cycle when emitted, otherwise low. `res0` and `res1` are output data ports that have valid data after when written to, otherwise DC (don't care). Note that we don't have any validation check for input ports. The protocol should be handled by the designer. The whole body is guarded by `forever` tag, which is a shorthand for `while (true) {func-body}`. The module is sequential and reentrant.

Then in the body, we first instantiate the required components:
```python
ddr_reader = DDRReader::new(outstanding=2)
dsp0 = DSP::new(func=mac)
dsp1 = DSP::new(func=mac)
buf0 = Buffer::new(size=256, width=32, cyclic=2)
buf1 = Buffer::new(size=256, width=32, cyclic=2)
```
The modules can be defined from some external Verilog library or a standard library with well-defined interface.

```python
G = bind(await enable)
base_addr_val = read base_addr @G
len_val = read len @G   # for simplicity, we assume len is multiple of 256
total_batches = len_val / 256

# launch first batch read
@G {
    emit ddr_reader.req
    write ddr_reader.addr = base_addr_val
    write ddr_reader.burst_len = 256
} @G
```
`bind()` returns the time when the event happens, in this case, when `enable` is high. At the same cycle `G`, we read `base_addr` and `len` input ports. This is the same as function call semantics except that it's caller and callee's responsibility to ensure the ports are valid at that time. Note that we don't specify the timestamp for `total_batches`. The compiler will infer it based on the dependencies. `@G {...} @H` is a timed region that schedules all operations inside to happen between timestamp G and H. Here we launch the first DDR read request at timestamp G.

Then we enter the main processing loop:
```python
for (i = 0, H = G; i < total_batches; i = i + 1, H = max(DDR_DONE, DSP_DONE) + 1) {
    buf_cur = buf0 if (i % 2 == 0) else buf1    # instance reference
    buf_next = buf1 if (i % 2 == 0) else buf0

    # launch next batch read
    if (i + 1 < total_batches) {
        @H {
            emit ddr_reader.req
            write ddr_reader.addr = base_addr_val + (i + 1) * 256 * 4   # 4 bytes per word
            write ddr_reader.burst_len = 256
        } @H
    }

    # read data from DDR and feed to buf_cur
    H_DDR = bind(await ddr_reader.resp_valid)   # wait for DDR read response
    for (j = 0, K = H_DDR; j < 256; j = j + 1, K = K + 1) {
        # for simplicity, we assume ddr_reader.data is ready every cycle after resp_valid
        data = read ddr_reader.data @K
        buf_cur.store(data, j) @K
    } @DDR_DONE

    emit batch_done @(H + DSP.LATENCY)
    # feed data from buf_next to dsps
    for (j = 0, K = H; j < 256; j = j + 2, K = K + DSP.II) {
        @K {    # for simplicity, we assume Buffer load/store is combinational
            write dsp0.in0 = buf_next.load(j + 0)
            write dsp1.in0 = buf_next.load(j + 1)
        } @K

        @(K + DSP.LATENCY) {   # wait for DSP to finish
            res_0 = read dsp0.out
            res_1 = read dsp1.out

            write res0 = res_0
            write res1 = res_1
        } @(K + DSP.LATENCY)
    } @DSP_DONE

}
```



```python
def ddr_read_compute(
    enable: rs.InputPulse,
    base_addr: rs.Input[32],
    len: rs.Input[32],
    batch_done: rs.OutputPulse,
    res0: rs.Output[64],
    res1: rs.Output[64],
    res2: rs.Output[64],
    res3: rs.Output[64]
) forever { # forever is shorthand for "while (true) {func-body}"
    # instances
    ddr_reader = DDRReader::new(outstanding=2)
    dsps = [DSP::new(func=mac) for _ in range(4)]
    buf0 = Buffer::new(size=256, width=32, cyclic=4)
    buf1 = Buffer::new(size=256, width=32, cyclic=4)

    G = bind(await enable)
    base_addr_val = read base_addr @G
    len_val = read len @G   # for simplicity, we assume len is multiple of 256
    total_batches = len_val / 256

    # launch first batch read
    @G {
        emit ddr_reader.req
        write ddr_reader.addr = read base_addr_val
        write ddr_reader.burst_len = 256
    } @G

    for (i = 0, H = G; i < total_batches; i = i + 1, H = max(DDR_DONE, DSP_DONE)) {
        buf_cur = buf0 if (i % 2 == 0) else buf1    # instance reference
        buf_next = buf1 if (i % 2 == 0) else buf0

        # launch next batch read
        if (i + 1 < total_batches) {
            @H {
                emit ddr_reader.req
                write ddr_reader.addr = base_addr_val + (i + 1) * 256 * 4   # 4 bytes per word
                write ddr_reader.burst_len = 256
            } @H
        }

        # read data from DDR and feed to buf_cur
        H_DDR = bind(await ddr_reader.resp_valid)   # wait for DDR read response
        for (j = 0, K = H_DDR; j < 256; j = j + 1, K = K + 1) {
            # for simplicity, we assume ddr_reader.data is ready every cycle after resp_valid
            data = read ddr_reader.data @K
            buf_cur.store(data, j) @K
        } @DDR_DONE

        emit batch_done @(H + DSP.LATENCY)
        # feed data from buf_next to dsps
        for (j = 0, K = H; j < 256; j = j + 4, K = K + DSP.II) {
            @K {    # for simplicity, we assume Buffer load/store is combinational
                write dsps[0].in0 = buf_next.load(j + 0)
                write dsps[1].in0 = buf_next.load(j + 1)
                write dsps[2].in0 = buf_next.load(j + 2)
                write dsps[3].in0 = buf_next.load(j + 3)
            } @K

            @(K + DSP.LATENCY) {   # wait for DSP to finish
                res_0 = read dsps[0].out
                res_1 = read dsps[1].out
                res_2 = read dsps[2].out
                res_3 = read dsps[3].out

                write res0 = res_0
                write res1 = res_1
                write res2 = res_2
                write res3 = res_3
            } @(K + DSP.LATENCY)
        } @DSP_DONE

    }
}
```
