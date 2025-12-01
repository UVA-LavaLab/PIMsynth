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

module mul_fp16 
#(
    parameter IMPL_TYPE = 0
)
(
    input wire [15:0] a,      // First operand (IEEE-754 format)
    input wire [15:0] b,      // Second operand (IEEE-754 format)
    
    output wire [15:0] result  // Final result
);

    // Sign calculation
    wire result_sign = a[15] ^ b[15];
    
    // Exception flag sets 1 if either one of the exponent is 255
    wire a_is_exception = (&a[14:10]);
    wire b_is_exception = (&b[14:10]);
    wire is_exception = a_is_exception | b_is_exception;
    
    wire a_is_zero = ~|a[14:10] & ~|a[9:0];
    wire b_is_zero = ~|b[14:10] & ~|b[9:0];

    // nan detection: NaN occurs when either operand is NaN (exp=255 with non-zero mantissa)
    wire a_is_nan = (&a[14:10]) & (|a[9:0]);
    wire b_is_nan = (&b[14:10]) & (|b[9:0]);

    wire is_nan = a_is_nan | b_is_nan | (a_is_zero & b_is_exception) | (b_is_zero & a_is_exception);


    // Assigning significand values according to Hidden Bit
    wire [10:0] a_significand = (|a[14:10]) ? {1'b1, a[9:0]} : {1'b0, a[9:0]};
    wire [10:0] b_significand = (|b[14:10]) ? {1'b1, b[9:0]} : {1'b0, b[9:0]};
    
    // Calculate product (11x11 -> 22-bit) using custom multiplier
    wire [21:0] product;
    multiplier_nbit_full #(.WIDTH(11), .IMPL_TYPE(IMPL_TYPE)) u_multiplier (
        .A(a_significand),
        .B(b_significand),
        .P(product)
    );
    
    // Product round: ending 22 bits are OR'ed for rounding operation
    wire product_round = |product_normalised[21:0];
    
    // Normalization check
    wire is_normalised = product[9];
    wire [21:0] product_normalised = is_normalised ? product : product << 1;

    // Final Mantissa
    // Use adder_nbit_cin for mantissa addition (product_normalised[20:11] + rounding)
    wire [10:0] product_mantissa;
    adder_nbit_cin #(.WIDTH(11)) u_mantissa_adder (
        .A({{1'b0}, {product_normalised[20:11]}}),
        .B({{10'b0}, {(product_normalised[10] & product_round)}}),
        .Cin(1'b0),
        .Sum(product_mantissa)
    );
    wire is_renormalized = product_mantissa[10] ? 1'b1 : 1'b0;

    // Zero detection
    wire is_zero = is_exception ? 1'b0 : (product_normalised[21:10] == 11'd0) ? 1'b1 : 1'b0;
    
    // Sum of exponents
    // Use adder_nbit for summing exponents
    wire [5:0] sum_exponent;
    adder_nbit_cin #(.WIDTH(6)) u_exponent_adder (
        .A({1'b0, a[14:10]}),
        .B({1'b0, b[14:10]}),
        .Cin(1'b0),
        .Sum(sum_exponent)
    );
    
    // Final exponent calculation
    // assign exponent = sum_exponent - 5'd15 + normalised + renormalized; (TODO: delete this)
    // -15 = +6'h31 in two's complement (for 6-bit arithmetic)
    wire [5:0] bias   = 6'h31;
    wire [1:0] k      = { (is_normalised & is_renormalized), (is_normalised ^ is_renormalized) }; // 0..2
    wire [5:0] k_ext  = {4'b0, k};

    // Implement exponent = sum_exponent + bias + k_ext using two adder_nbit_cin instances
    wire [5:0] exponent_tmp1;  // sum_exponent + bias
    wire [5:0] exponent;
    adder_nbit_cin #(.WIDTH(6)) u_exp_bias_adder (
        .A(sum_exponent),
        .B(bias),       // bias is 6 bits, pad to 6
        .Cin(1'b0),
        .Sum(exponent_tmp1)
    );
    adder_nbit_cin #(.WIDTH(6)) u_exp_kext_adder (
        .A(exponent_tmp1),
        .B(k_ext),      // k_ext is 6 bits, pad to 6
        .Cin(1'b0),
        .Sum(exponent)
    );
    
    // Overflow detection: If overall exponent is greater (or equal) to 31 then Overflow condition
    wire exp_gt_31 = exponent[5] & ~exponent[4];   // >31: bit6=1 AND bit5=0 
    wire exp_eq_31 = ~exponent[5] & (&exponent[4:0]); // 31: bit5=0, all lower bits=1
    wire is_overflow = !is_zero & (exp_gt_31 | exp_eq_31);
    
    // Underflow detection: If exponent is less than 0 then Underflow condition
    wire is_underflow = (exponent[5] & exponent[4] & !is_zero) ? 1'b1 : 1'b0;
    
    // Final result - IEEE-754 priority order
    assign result = 
                    is_nan        ? {result_sign, 5'h1F, 10'h3FF} :                    // NaN
                    is_overflow   ? {result_sign, 5'h1F, 10'h0} :                // Infinity
                    is_underflow  ? {result_sign, 5'h0, 10'h0} :                        // Zero (underflow)
                    is_zero       ? {result_sign, 15'h0} :                        // Zero (normal)
                    is_exception  ? {result_sign, 5'h1F, 10'h0} :                  // Infinity (inf × inf, inf × normal)
                    {result_sign, exponent[4:0], product_mantissa[9:0]};      // Normal result

endmodule

