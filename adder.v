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
    wire[32:0] tmp12;
    wire[31:0] tmp13;
    wire[31:0] tmp14;
    wire[31:0] tmp15;
    wire tmp16;
    wire tmp17;
    wire[30:0] tmp18;
    wire[31:0] tmp19;
    wire[31:0] tmp20;
    wire tmp21;
    wire[1:0] tmp22;
    wire tmp23;
    wire tmp24;
    wire tmp25;
    wire tmp26;
    wire tmp27;
    wire tmp28;
    wire tmp29;
    wire[1:0] tmp30;
    wire[2:0] tmp31;
    wire[1:0] tmp32;
    wire tmp33;
    wire tmp34;
    wire tmp35;
    wire[1:0] tmp36;
    wire[1:0] tmp37;
    wire[1:0] tmp38;

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
    assign done = tmp17;
    assign result = tmp20;
    assign tmp2 = tmp13;
    assign tmp4 = {const_1_0};
    assign tmp5 = {tmp4, const_0_0};
    assign tmp6 = cnter == tmp5;
    assign tmp7 = tmp6 & go;
    assign tmp8 = tmp7 ? a : tmp0;
    assign tmp9 = {const_3_0};
    assign tmp10 = {tmp9, const_2_1};
    assign tmp11 = cnter == tmp10;
    assign tmp12 = tmp0 + b;
    assign tmp13 = {tmp12[31], tmp12[30], tmp12[29], tmp12[28], tmp12[27], tmp12[26], tmp12[25], tmp12[24], tmp12[23], tmp12[22], tmp12[21], tmp12[20], tmp12[19], tmp12[18], tmp12[17], tmp12[16], tmp12[15], tmp12[14], tmp12[13], tmp12[12], tmp12[11], tmp12[10], tmp12[9], tmp12[8], tmp12[7], tmp12[6], tmp12[5], tmp12[4], tmp12[3], tmp12[2], tmp12[1], tmp12[0]};
    assign tmp14 = tmp11 ? b : tmp1;
    assign tmp15 = tmp11 ? tmp2 : tmp3;
    assign tmp16 = cnter == const_4_2;
    assign tmp17 = cnter == const_5_2;
    assign tmp18 = {const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0};
    assign tmp19 = {tmp18, const_6_0};
    assign tmp20 = tmp16 ? tmp3 : tmp19;
    assign tmp21 = {const_9_0};
    assign tmp22 = {tmp21, const_8_0};
    assign tmp23 = cnter == tmp22;
    assign tmp24 = tmp23 & go;
    assign tmp25 = cnter < const_11_2;
    assign tmp26 = ~tmp25;
    assign tmp27 = ~tmp23;
    assign tmp28 = tmp27 & tmp26;
    assign tmp29 = {const_14_0};
    assign tmp30 = {tmp29, const_13_1};
    assign tmp31 = cnter + tmp30;
    assign tmp32 = {tmp31[1], tmp31[0]};
    assign tmp33 = ~tmp23;
    assign tmp34 = ~tmp26;
    assign tmp35 = tmp33 & tmp34;
    assign tmp36 = tmp24 ? const_10_1 : cnter;
    assign tmp37 = tmp28 ? const_12_0 : tmp36;
    assign tmp38 = tmp35 ? tmp32 : tmp37;

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
            cnter <= tmp38;
            tmp0 <= tmp8;
            tmp1 <= tmp14;
            tmp3 <= tmp15;
        end
    end

endmodule

