// n-bit Unsigned Integer Less Than Submodule
// Dependencies: subtractor_1bit_cmp.v
// deyuan, 03/30/2025

module lt_uint_nbit #(
    parameter WIDTH = 32
)(
    input [WIDTH-1:0] A,
    input [WIDTH-1:0] B,
    output Y
);

    wire [WIDTH:0] Borrow;
    assign Borrow[0] = 1'b0; // Initialize the first borrow bit to 0

    // Instantiate a chain of cmp subtractor modules
    genvar i;
    generate
        for (i = 0; i < WIDTH; i = i + 1) begin : subtractor_cmp_chain
            subtractor_1bit_cmp u_subtractor_1bit_cmp (
                .A(A[i]),
                .B(B[i]),
                .Bin(Borrow[i]),
                .Bout(Borrow[i+1])
            );
        end
    endgenerate

    // A < B if the last borrow bit is 1
    assign Y = Borrow[WIDTH];

endmodule