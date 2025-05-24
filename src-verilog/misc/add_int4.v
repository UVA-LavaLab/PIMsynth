// 4-bit Integer Addition
// Dependencies: adder_1bit.v adder_nbit.v
// deyuan, 05/24/2025

module add_int4 #(
    parameter WIDTH = 4
)(
    input [WIDTH-1:0] A,
    input [WIDTH-1:0] B,
    output [WIDTH-1:0] Sum
);
    adder_nbit #(
        .WIDTH(WIDTH)
    ) u_adder_nbit (
        .A(A),
        .B(B),
        .Sum(Sum)
    );
endmodule
