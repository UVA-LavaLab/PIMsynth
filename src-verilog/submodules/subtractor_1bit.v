// 1-bit Full Subtractor Submodule
// Dependencies: None
// deyuan, 03/28/2025

module subtractor_1bit (
    input A,
    input B,
    input Bin,
    output Sub,
    output Bout
);

    wire tmp;

    // XOR + MUX
    assign tmp = A ^ Bin;
    assign Bout = tmp ? Bin : B;
    assign Sub = tmp ^ B;

endmodule
