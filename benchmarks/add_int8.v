// 8-bit Integer Addition
// Dependencies: adder_1bit.v adder_nbit.v
// deyuan, 03/28/2025

module add_int8 #(
    parameter WIDTH = 8
)(
    input [WIDTH-1:0] A,
    input [WIDTH-1:0] B,
    output [WIDTH-1:0] Sum
);
    adder_nbit #(
        .WIDTH(WIDTH)
    ) adder_inst (
        .A(A),
        .B(B),
        .Sum(Sum)
    );
endmodule
