// 16-bit Integer Abs
// Dependencies: abs_nbit.v adder_1bit_half.v
// deyuan, 03/29/2025

module abs_int16 #(
    parameter WIDTH = 16
)(
    input [WIDTH-1:0] A,
    output [WIDTH-1:0] Y
);

    abs_nbit #(
        .WIDTH(WIDTH)
    ) u_abs_nbit (
        .A(A),
        .Y(Y)
    );

endmodule
