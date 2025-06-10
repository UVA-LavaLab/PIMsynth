// 4-bit Unsigned Integer Multiplication
// Dependencies: adder_1bit_half.v adder_1bit.v adder_nbit.v mul_full_2bit.v mul_partial_2bit.v mul_partial_4bit.v mul_full_4bit.v mul_partial_8bit.v
// hosein, 06/10/2025

module mul_uint8(
    input  [7:0] A,  // Multiplicand
    input  [7:0] B,  // Multiplier
    output [7:0] P   // Lower 4 bits of the approximate product
);
    mul_partial_8bit u0 (.A(A), .B(B), .P(P));
endmodule

