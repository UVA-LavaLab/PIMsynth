// int32 add-sub
// deyuan, 09/30/2024

module add_sub_int32(input [31:0] a, input [31:0] b, input [31:0] c, output [31:0] result);
    assign result = a + b - c;
endmodule

