// 1-bit Subtractor Submodule for Comparison
// Dependencies: None
// deyuan, 03/30/2025

module subtractor_1bit_cmp (
    input A,
    input B,
    input Bin,
    output Bout
);

    wire tmp;

    // XOR + MUX
    assign tmp = A ^ Bin;
    assign Bout = tmp ? Bin : B;

endmodule
