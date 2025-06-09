module mul_uint4(
    input  [3:0] A,  // Multiplicand
    input  [3:0] B,  // Multiplier
    output [3:0] P   // Lower 4 bits of the approximate product
);

    wire [1:0] A_lo = A[1:0];
    wire [1:0] A_hi = A[3:2];
    wire [1:0] B_lo = B[1:0];
    wire [1:0] B_hi = B[3:2];

    wire [3:0] M0, M1, M2;
    wire [4:0] M1_plus_M2;
    wire [7:0] shifted_middle, extended_M0;
    wire [7:0] full_sum;

    // 2-bit multipliers using multiplier_nbit
    multiplier_nbit #(2) u0 (.A(A_lo), .B(B_lo), .P(M0));
    multiplier_nbit #(2) u1 (.A(A_hi), .B(B_lo), .P(M1));
    multiplier_nbit #(2) u2 (.A(A_lo), .B(B_hi), .P(M2));

    // Add M1 + M2 using adder_nbit #(5)
    adder_nbit #(5) u_adder_mid (
        .A({1'b0, M1}), 
        .B({1'b0, M2}), 
        .Sum(M1_plus_M2)
    );

    // Shift (M1+M2)<<2 and zero-extend M0
    assign shifted_middle = {M1_plus_M2, 2'b00};
    assign extended_M0 = {4'b0000, M0};

    // Final sum using adder_nbit #(8)
    adder_nbit #(8) u_adder_final (
        .A(shifted_middle),
        .B(extended_M0),
        .Sum(full_sum)
    );

    assign P = full_sum[3:0]; // Truncate to lower 4 bits

endmodule

