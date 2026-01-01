// Generated automatically via PyRTL
// As one initial test of synthesis, map to FPGA with:
//   yosys -p "synth_xilinx -top toplevel" thisfile.v

module toplevel(clk, rst, a, b, go, done, result);
    input clk;
    input rst;
    input[31:0] a;
    input[31:0] b;
    input go;
    output done;
    output[31:0] result;

    reg[1:0] cnter;
    reg[31:0] tmp0;
    reg[31:0] tmp1;
    reg[31:0] tmp3;

    wire const_0_0;
    wire const_1_0;
    wire const_2_1;
    wire const_3_0;
    wire[1:0] const_4_2;
    wire[1:0] const_5_2;
    wire const_6_0;
    wire const_7_0;
    wire const_8_0;
    wire const_9_0;
    wire[1:0] const_10_1;
    wire[1:0] const_11_2;
    wire[1:0] const_12_0;
    wire const_13_1;
    wire const_14_0;
    wire[31:0] tmp2;
    wire tmp4;
    wire[1:0] tmp5;
    wire tmp6;
    wire tmp7;
    wire[31:0] tmp8;
    wire tmp9;
    wire[1:0] tmp10;
    wire tmp11;
    wire tmp12;
    wire[32:0] tmp13;
    wire[31:0] tmp14;
    wire[31:0] tmp15;
    wire[31:0] tmp16;
    wire tmp17;
    wire tmp18;
    wire tmp19;
    wire tmp20;
    wire[30:0] tmp21;
    wire[31:0] tmp22;
    wire[31:0] tmp23;
    wire tmp24;
    wire[1:0] tmp25;
    wire tmp26;
    wire tmp27;
    wire tmp28;
    wire tmp29;
    wire tmp30;
    wire tmp31;
    wire tmp32;
    wire[1:0] tmp33;
    wire[2:0] tmp34;
    wire[1:0] tmp35;
    wire tmp36;
    wire tmp37;
    wire tmp38;
    wire[1:0] tmp39;
    wire[1:0] tmp40;
    wire[1:0] tmp41;

    // Combinational
    assign const_0_0 = 0;
    assign const_1_0 = 0;
    assign const_2_1 = 1;
    assign const_3_0 = 0;
    assign const_4_2 = 2;
    assign const_5_2 = 2;
    assign const_6_0 = 0;
    assign const_7_0 = 0;
    assign const_8_0 = 0;
    assign const_9_0 = 0;
    assign const_10_1 = 1;
    assign const_11_2 = 2;
    assign const_12_0 = 0;
    assign const_13_1 = 1;
    assign const_14_0 = 0;
    assign done = tmp20;
    assign result = tmp23;
    assign tmp2 = tmp14;
    assign tmp4 = {const_1_0};
    assign tmp5 = {tmp4, const_0_0};
    assign tmp6 = cnter == tmp5;
    assign tmp7 = tmp6 | go;
    assign tmp8 = tmp7 ? a : tmp0;
    assign tmp9 = {const_3_0};
    assign tmp10 = {tmp9, const_2_1};
    assign tmp11 = cnter == tmp10;
    assign tmp12 = tmp11 | go;
    assign tmp13 = tmp0 + b;
    assign tmp14 = {tmp13[31], tmp13[30], tmp13[29], tmp13[28], tmp13[27], tmp13[26], tmp13[25], tmp13[24], tmp13[23], tmp13[22], tmp13[21], tmp13[20], tmp13[19], tmp13[18], tmp13[17], tmp13[16], tmp13[15], tmp13[14], tmp13[13], tmp13[12], tmp13[11], tmp13[10], tmp13[9], tmp13[8], tmp13[7], tmp13[6], tmp13[5], tmp13[4], tmp13[3], tmp13[2], tmp13[1], tmp13[0]};
    assign tmp15 = tmp12 ? b : tmp1;
    assign tmp16 = tmp12 ? tmp2 : tmp3;
    assign tmp17 = cnter == const_4_2;
    assign tmp18 = tmp17 | go;
    assign tmp19 = cnter == const_5_2;
    assign tmp20 = tmp19 | go;
    assign tmp21 = {const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0};
    assign tmp22 = {tmp21, const_6_0};
    assign tmp23 = tmp18 ? tmp3 : tmp22;
    assign tmp24 = {const_9_0};
    assign tmp25 = {tmp24, const_8_0};
    assign tmp26 = cnter == tmp25;
    assign tmp27 = tmp26 & go;
    assign tmp28 = cnter < const_11_2;
    assign tmp29 = ~tmp28;
    assign tmp30 = ~tmp26;
    assign tmp31 = tmp30 & tmp29;
    assign tmp32 = {const_14_0};
    assign tmp33 = {tmp32, const_13_1};
    assign tmp34 = cnter + tmp33;
    assign tmp35 = {tmp34[1], tmp34[0]};
    assign tmp36 = ~tmp26;
    assign tmp37 = ~tmp29;
    assign tmp38 = tmp36 & tmp37;
    assign tmp39 = tmp27 ? const_10_1 : cnter;
    assign tmp40 = tmp31 ? const_12_0 : tmp39;
    assign tmp41 = tmp38 ? tmp35 : tmp40;

    // Registers
    always @(posedge clk)
    begin
        if (rst) begin
            cnter <= 0;
            tmp0 <= 0;
            tmp1 <= 0;
            tmp3 <= 0;
        end
        else begin
            cnter <= tmp41;
            tmp0 <= tmp8;
            tmp1 <= tmp15;
            tmp3 <= tmp16;
        end
    end

endmodule

