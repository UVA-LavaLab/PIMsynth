// 32-bit Unsigned Integer Greater Than
// Dependencies: gt_uint_nbit.v subtractor_1bit_cmp.v
// deyuan, 03/30/2025

module gt_uint32 #(
    parameter WIDTH = 32
)(
    input [WIDTH-1:0] A,
    input [WIDTH-1:0] B,
    output Y
);

    gt_uint_nbit #(
        .WIDTH(WIDTH)
    ) u_gt_uint_nbit (
        .A(A),
        .B(B),
        .Y(Y)
    );

endmodule
