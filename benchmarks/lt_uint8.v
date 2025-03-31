// 8-bit Unsigned Integer Less Than
// Dependencies: lt_uint_nbit.v subtractor_1bit_cmp.v
// deyuan, 03/30/2025

module lt_uint8 #(
    parameter WIDTH = 8
)(
    input [WIDTH-1:0] A,
    input [WIDTH-1:0] B,
    output Y
);

    lt_uint_nbit #(
        .WIDTH(WIDTH)
    ) u_lt_uint_nbit (
        .A(A),
        .B(B),
        .Y(Y)
    );

endmodule