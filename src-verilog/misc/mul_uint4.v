// 4-bit Unsigned Integer Multiplication
// Dependencies: adder_1bit_half.v adder_1bit.v adder_nbit.v mul_full_2bit.v mul_partal_2bit.v mul_partial_4bit.v
// hosein, 06/10/2025

module mul_uint4(
    input  [3:0] A,  // Multiplicand
    input  [3:0] B,  // Multiplier
    output [3:0] P   // Lower 4 bits of the approximate product
);
    mul_partial_4bit u0 (.A(A), .B(B), .P(P));
endmodule

