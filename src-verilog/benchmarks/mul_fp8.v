// IEEE-754 Single Precision Floating Point Multiplier - Combinational Logic
// Based on the implementation by Sheetal Swaroop Burada
// Pure combinational floating-point multiplication
// Dependencies: multiplier_nbit_full.v
//             : adder_nbit_cin.v
//             : adder_1bit.v
//             : maj3.v
// hosein, 10/18/2025

/* verilator lint_off UNUSEDSIGNAL */
/* verilator lint_off WIDTHEXPAND */

module mul_fp8 
#(
    parameter IMPL_TYPE = 0
)
(
    input wire [7:0] a,      // First operand (IEEE-754 format)
    input wire [7:0] b,      // Second operand (IEEE-754 format)
    
    output wire [7:0] result  // Final result
);

    // Sign calculation
    wire result_sign = a[7] ^ b[7];
    
    // Exception flag sets 1 if either one of the exponent is 255
    wire a_is_exception = (&a[6:4]);
    wire b_is_exception = (&b[6:4]);
    wire is_exception = a_is_exception | b_is_exception;
    
    wire a_is_zero = ~|a[6:4] & ~|a[3:0];
    wire b_is_zero = ~|b[6:4] & ~|b[3:0];

    // nan detection: NaN occurs when either operand is NaN (exp=255 with non-zero mantissa)
    wire a_is_nan = (&a[6:4]) & (|a[3:0]);
    wire b_is_nan = (&b[6:4]) & (|b[3:0]);

    wire is_nan = a_is_nan | b_is_nan | (a_is_zero & b_is_exception) | (b_is_zero & a_is_exception);


    // Assigning significand values according to Hidden Bit
    wire [4:0] a_significand = (|a[6:4]) ? {1'b1, a[3:0]} : {1'b0, a[3:0]};
    wire [4:0] b_significand = (|b[6:4]) ? {1'b1, b[3:0]} : {1'b0, b[3:0]};
    
    // Calculate product (5x5 -> 10-bit) using custom multiplier
    wire [9:0] product;
    multiplier_nbit_full #(.WIDTH(5), .IMPL_TYPE(IMPL_TYPE)) u_multiplier (
        .A(a_significand),
        .B(b_significand),
        .P(product)
    );
    
    // Product round: ending 9 bits are OR'ed for rounding operation
    wire product_round = |product_normalised[9:0];
    
    // Normalization check
    wire is_normalised = product[9];
    wire [9:0] product_normalised = is_normalised ? product : product << 1;

    // Final Mantissa
    // Use adder_nbit_cin for mantissa addition (product_normalised[8:5] + rounding)
    wire [4:0] product_mantissa;
    adder_nbit_cin #(.WIDTH(5)) u_mantissa_adder (
        .A({{1'b0}, {product_normalised[8:5]}}),
        .B({{4'b0}, {(product_normalised[4] & product_round)}}),
        .Cin(1'b0),
        .Sum(product_mantissa)
    );
    wire is_renormalized = product_mantissa[4] ? 1'b1 : 1'b0;

    // Zero detection
    wire is_zero = is_exception ? 1'b0 : (product_normalised[9:5] == 5'd0) ? 1'b1 : 1'b0;
    
    // Sum of exponents
    // Use adder_nbit for summing exponents
    wire [3:0] sum_exponent;
    adder_nbit_cin #(.WIDTH(4)) u_exponent_adder (
        .A({1'b0, a[6:4]}),
        .B({1'b0, b[6:4]}),
        .Cin(1'b0),
        .Sum(sum_exponent)
    );
    
    // Final exponent calculation
    // assign exponent = sum_exponent - 3'd3 + normalised + renormalized; (TODO: delete this)
    // -3 = +4'hd in two's complement (for 4-bit arithmetic)
    wire [3:0] bias   = 4'hd;
    wire [1:0] k      = { (is_normalised & is_renormalized), (is_normalised ^ is_renormalized) }; // 0..2
    wire [3:0] k_ext  = {2'b0, k};

    // Implement exponent = sum_exponent + bias + k_ext using two adder_nbit_cin instances
    wire [3:0] exponent_tmp1;  // sum_exponent + bias
    wire [3:0] exponent;
    adder_nbit_cin #(.WIDTH(4)) u_exp_bias_adder (
        .A(sum_exponent),
        .B(bias),       // bias is 8 bits, pad to 9
        .Cin(1'b0),
        .Sum(exponent_tmp1)
    );
    adder_nbit_cin #(.WIDTH(4)) u_exp_kext_adder (
        .A(exponent_tmp1),
        .B(k_ext),      // k_ext is 4 bits, pad to 4
        .Cin(1'b0),
        .Sum(exponent)
    );
    
    // Overflow detection: If overall exponent is greater (or equal) to 7 then Overflow condition
    wire exp_gt_7 = exponent[3] & ~exponent[2];   // >7: bit4=1 AND bit3=0 
    wire exp_eq_7 = ~exponent[3] & (&exponent[2:0]); // 7: bit4=0, all lower bits=1
    wire is_overflow = !is_zero & (exp_gt_7 | exp_eq_7);
    
    // Underflow detection: If exponent is less than 0 then Underflow condition
    wire is_underflow = (exponent[3] & exponent[2] & !is_zero) ? 1'b1 : 1'b0;
    
    // Final result - IEEE-754 priority order
    assign result = 
                    is_nan        ? {result_sign, 3'h7, 4'hF} :                    // NaN
                    is_overflow   ? {result_sign, 3'h7, 4'h0} :                // Infinity
                    is_underflow  ? {result_sign, 3'h0, 4'h0} :                        // Zero (underflow)
                    is_zero       ? {result_sign, 7'h0} :                        // Zero (normal)
                    is_exception  ? {result_sign, 3'h7, 4'h0} :                  // Infinity (inf × inf, inf × normal)
                    {result_sign, exponent[2:0], product_mantissa[3:0]};      // Normal result

endmodule

