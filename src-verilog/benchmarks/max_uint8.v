// 8-bit Unsigned Integer Max
// Dependencies: gt_uint_nbit.v subtractor_1bit_cmp.v
// deyuan, 03/30/2025

module max_uint8 #(
    parameter WIDTH = 8
)(
    input [WIDTH-1:0] A,
    input [WIDTH-1:0] B,
    output [WIDTH-1:0] Y,
);

    wire gt;
    gt_uint_nbit #(
        .WIDTH(WIDTH)
    ) u_gt_uint_nbit (
        .A(A),
        .B(B),
        .Y(gt)
    );

    assign Y = gt ? A : B;

endmodule
