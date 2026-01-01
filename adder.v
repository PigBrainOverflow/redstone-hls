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

    reg active;
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
    wire const_9_1;
    wire[1:0] const_10_1;
    wire[1:0] const_11_2;
    wire const_12_0;
    wire[1:0] const_13_2;
    wire const_14_1;
    wire const_15_0;
    wire[31:0] tmp2;
    wire tmp4;
    wire[1:0] tmp5;
    wire tmp6;
    wire tmp7;
    wire tmp8;
    wire[31:0] tmp9;
    wire tmp10;
    wire[1:0] tmp11;
    wire tmp12;
    wire tmp13;
    wire tmp14;
    wire[32:0] tmp15;
    wire[31:0] tmp16;
    wire[31:0] tmp17;
    wire[31:0] tmp18;
    wire tmp19;
    wire tmp20;
    wire tmp21;
    wire tmp22;
    wire tmp23;
    wire tmp24;
    wire[30:0] tmp25;
    wire[31:0] tmp26;
    wire[31:0] tmp27;
    wire tmp28;
    wire tmp29;
    wire tmp30;
    wire tmp31;
    wire tmp32;
    wire tmp33;
    wire tmp34;
    wire tmp35;
    wire tmp36;
    wire[1:0] tmp37;
    wire[2:0] tmp38;
    wire[1:0] tmp39;
    wire tmp40;
    wire tmp41;
    wire tmp42;
    wire tmp43;
    wire tmp44;
    wire tmp45;
    wire tmp46;
    wire[1:0] tmp47;
    wire[1:0] tmp48;

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
    assign const_9_1 = 1;
    assign const_10_1 = 1;
    assign const_11_2 = 2;
    assign const_12_0 = 0;
    assign const_13_2 = 2;
    assign const_14_1 = 1;
    assign const_15_0 = 0;
    assign done = tmp24;
    assign result = tmp27;
    assign tmp2 = tmp16;
    assign tmp4 = {const_1_0};
    assign tmp5 = {tmp4, const_0_0};
    assign tmp6 = cnter == tmp5;
    assign tmp7 = active | go;
    assign tmp8 = tmp6 & tmp7;
    assign tmp9 = tmp8 ? a : tmp0;
    assign tmp10 = {const_3_0};
    assign tmp11 = {tmp10, const_2_1};
    assign tmp12 = cnter == tmp11;
    assign tmp13 = active | go;
    assign tmp14 = tmp12 & tmp13;
    assign tmp15 = tmp0 + b;
    assign tmp16 = {tmp15[31], tmp15[30], tmp15[29], tmp15[28], tmp15[27], tmp15[26], tmp15[25], tmp15[24], tmp15[23], tmp15[22], tmp15[21], tmp15[20], tmp15[19], tmp15[18], tmp15[17], tmp15[16], tmp15[15], tmp15[14], tmp15[13], tmp15[12], tmp15[11], tmp15[10], tmp15[9], tmp15[8], tmp15[7], tmp15[6], tmp15[5], tmp15[4], tmp15[3], tmp15[2], tmp15[1], tmp15[0]};
    assign tmp17 = tmp14 ? b : tmp1;
    assign tmp18 = tmp14 ? tmp2 : tmp3;
    assign tmp19 = cnter == const_4_2;
    assign tmp20 = active | go;
    assign tmp21 = tmp19 & tmp20;
    assign tmp22 = cnter == const_5_2;
    assign tmp23 = active | go;
    assign tmp24 = tmp22 & tmp23;
    assign tmp25 = {const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0, const_7_0};
    assign tmp26 = {tmp25, const_6_0};
    assign tmp27 = tmp21 ? tmp3 : tmp26;
    assign tmp28 = active == const_8_0;
    assign tmp29 = tmp28 & go;
    assign tmp30 = tmp28 & go;
    assign tmp31 = cnter == const_11_2;
    assign tmp32 = ~tmp28;
    assign tmp33 = tmp32 & active;
    assign tmp34 = tmp33 & tmp31;
    assign tmp35 = cnter < const_13_2;
    assign tmp36 = {const_15_0};
    assign tmp37 = {tmp36, const_14_1};
    assign tmp38 = cnter + tmp37;
    assign tmp39 = {tmp38[1], tmp38[0]};
    assign tmp40 = ~tmp28;
    assign tmp41 = tmp40 & active;
    assign tmp42 = ~tmp31;
    assign tmp43 = tmp41 & tmp42;
    assign tmp44 = tmp43 & tmp35;
    assign tmp45 = tmp29 ? const_9_1 : active;
    assign tmp46 = tmp34 ? const_12_0 : tmp45;
    assign tmp47 = tmp30 ? const_10_1 : cnter;
    assign tmp48 = tmp44 ? tmp39 : tmp47;

    // Registers
    always @(posedge clk)
    begin
        if (rst) begin
            active <= 0;
            cnter <= 0;
            tmp0 <= 0;
            tmp1 <= 0;
            tmp3 <= 0;
        end
        else begin
            active <= tmp46;
            cnter <= tmp48;
            tmp0 <= tmp9;
            tmp1 <= tmp17;
            tmp3 <= tmp18;
        end
    end

endmodule

