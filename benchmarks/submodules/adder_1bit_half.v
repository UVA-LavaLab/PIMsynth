// 1-bit Half Adder Submodule
// Dependencies: None
// deyuan, 03/29/2025

module adder_1bit_half (
    input A,
    input B,
    output Sum,
    output Cout
);

    assign Sum = A ^ B;
    assign Cout = A & B;

endmodule