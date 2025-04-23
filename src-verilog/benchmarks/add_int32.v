// 32-bit Integer Addition
// Dependencies: adder_1bit.v adder_nbit.v
// deyuan, 03/28/2025

module add_int32 #(
    parameter WIDTH = 32
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
