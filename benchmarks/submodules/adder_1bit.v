// 1-bit Full Adder Submodule
// Dependencies: None
// deyuan, 03/28/2025

module adder_1bit (
    input A,
    input B,
    input Cin,
    output Sum,
    output Cout
);

    wire tmp;

    // XOR + MUX
    assign tmp = A ^ Cin;
    assign Cout = tmp ? B : Cin;
    assign Sum = tmp ^ B;

endmodule
