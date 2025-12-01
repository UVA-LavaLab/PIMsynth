// n-bit Integer Multiplier Submodule
// Dependencies: adder_1bit.v adder_nbit_cin.v
// hosein, 10/06/2025

/* verilator lint_off UNUSEDPARAM */
/* verilator lint_off EOFNEWLINE */
/* verilator lint_off GENUNNAMED */

module multiplier_nbit_full #(
    parameter WIDTH = 32,
    parameter IMPL_TYPE = 0
)(
    input  [WIDTH-1:0] A,  // Multiplicand
    input  [WIDTH-1:0] B,  // Multiplier
    output [2*WIDTH-1:0] P // Full 2*WIDTH bits of the product
);

    // Custom multiplier implementation with 2*WIDTH output
    // Using generic generation with adder_nbit instead of native addition operators
    
    // Declare accumulator array using generate
    wire [2*WIDTH-1:0] acc [0:WIDTH-1];
    
    // Generate partial products and accumulator chain
    genvar i;
    generate
        // Initial accumulator (partial product 0)
        assign acc[0] = B[0] ? {{WIDTH{1'b0}}, A} : {2*WIDTH{1'b0}};
        
        // Generate chain of adders for remaining partial products
        for (i = 1; i < WIDTH; i = i + 1) begin : multiplier_chain
            // Partial product for bit B[i]
            wire [2*WIDTH-1:0] partial_product;
            assign partial_product = B[i] ? ({{WIDTH{1'b0}}, A} << i) : {2*WIDTH{1'b0}};
            
            // Add partial product to previous accumulator using custom adder
            adder_nbit_cin #(.WIDTH(2*WIDTH), .IMPL_TYPE(IMPL_TYPE)) u_adder (
                .A(acc[i-1]),
                .B(partial_product),
                .Cin(1'b0),
                .Sum(acc[i])
            );
        end
    endgenerate
    
    // Output the final result
    assign P = acc[WIDTH-1];

endmodule
