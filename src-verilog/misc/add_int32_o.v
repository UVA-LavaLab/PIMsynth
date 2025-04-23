// int32 add - with optimized full adder submodule
// deyuan, 11/23/2024

// 1-bit Full Adder
module FullAdder (
    input A,
    input B,
    input Cin,
    output Sum,
    output Cout
);

    wire AxorC;

    // XOR + MUX
    assign AxorC = A ^ Cin;
    assign Cout = AxorC ? B : A;
    assign Sum = AxorC ^ B;

endmodule

// 32-bit Adder with Cin initialized to 0 and no Cout
module Adder32 (
    input [31:0] A,
    input [31:0] B,
    output [31:0] Sum
);
    wire [31:0] Carry; // Internal carry signals

    // Instantiate the first full adder with Cin = 0
    FullAdder FA0 (
        .A(A[0]),
        .B(B[0]),
        .Cin(1'b0),    // Initialize Cin to 0
        .Sum(Sum[0]),
        .Cout(Carry[0])
    );

    // Instantiate the remaining 31 full adders
    genvar i;
    generate
        for (i = 1; i < 32; i = i + 1) begin : adder_chain
            FullAdder FA (
                .A(A[i]),
                .B(B[i]),
                .Cin(Carry[i-1]),
                .Sum(Sum[i]),
                .Cout(Carry[i])
            );
        end
    endgenerate
endmodule

