// 16-bit Signed Integer Less Than
// Dependencies: lt_int_nbit.v subtractor_1bit_cmp.v
// deyuan, 03/30/2025

module lt_int16 #(
    parameter WIDTH = 16
)(
    input [WIDTH-1:0] A,
    input [WIDTH-1:0] B,
    output Y
);

    lt_int_nbit #(
        .WIDTH(WIDTH)
    ) u_lt_int_nbit (
        .A(A),
        .B(B),
        .Y(Y)
    );

endmodule