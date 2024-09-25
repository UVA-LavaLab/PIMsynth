// int32 div/rem
// deyuan, 09/25/2024

module mul_int32(input [31:0] a, input [31:0] b, output [31:0] q, output [31:0] r);
    assign q = a / b;
    assign r = a % b;
endmodule

