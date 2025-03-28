// 16-bit Integer Multiplication
// Dependencies: adder_1bit.v adder_nbit.v
// deyuan, 03/28/2025

module mul_int16 #(
    parameter WIDTH = 16
)(
    input  [WIDTH-1:0] A,  // Multiplicand
    input  [WIDTH-1:0] B,  // Multiplier
    output [WIDTH-1:0] P   // Lower WIDTH bits of the product
);

    // Create partial products for each B[i]
    wire [WIDTH-1:0] acc [0:WIDTH];
    // Assigne initial value for acc[0]
    assign acc[0] = B[0] ? A : {WIDTH{1'b0}};
    
    // Generate a chain of bit-serial adders
    genvar i;
    generate
        for (i = 1; i < WIDTH; i = i + 1) begin : chain_adders
            assign acc[i][i:0] = acc[i-1][i:0];
            adder_nbit #(WIDTH-i) adder_inst (
                .A(B[i] ? A[WIDTH-1:i+1] : {WIDTH-i{1'b0}}),
                .B(acc[i-1][WIDTH-1:i+1]),
                .Sum(acc[i][WIDTH-1:i+1])
            );
        end
    endgenerate

    assign P = acc[WIDTH-1];

endmodule
