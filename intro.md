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
) {
    let G = await enable;   # wait for enable pulse, return the timestamp
    let n = n@G;    # read n at timestamp G
    let mut i = 0;
    let mut res = 0;
    while (i < n) {
        let a_i = a@(G + i + 1);   # read a[i] at timestamp G + i + 1
        let b_i = b@(G + i + 1);   # read b[i] at timestamp G + i + 1
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