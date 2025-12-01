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

module mul_fp32 
#(
    parameter IMPL_TYPE = 0
)
(
    input wire [31:0] a,      // First operand (IEEE-754 format)
    input wire [31:0] b,      // Second operand (IEEE-754 format)
    
    output wire [31:0] result  // Final result
);

    // Sign calculation
    wire result_sign = a[31] ^ b[31];
    
    // Exception flag sets 1 if either one of the exponent is 255
    wire a_is_exception = (&a[30:23]);
    wire b_is_exception = (&b[30:23]);
    wire is_exception = a_is_exception | b_is_exception;
    
    wire a_is_zero = ~|a[30:23] & ~|a[22:0];
    wire b_is_zero = ~|b[30:23] & ~|b[22:0];

    // nan detection: NaN occurs when either operand is NaN (exp=255 with non-zero mantissa)
    wire a_is_nan = (&a[30:23]) & (|a[22:0]);
    wire b_is_nan = (&b[30:23]) & (|b[22:0]);

    wire is_nan = a_is_nan | b_is_nan | (a_is_zero & b_is_exception) | (b_is_zero & a_is_exception);


    // Assigning significand values according to Hidden Bit
    wire [23:0] a_significand = (|a[30:23]) ? {1'b1, a[22:0]} : {1'b0, a[22:0]};
    wire [23:0] b_significand = (|b[30:23]) ? {1'b1, b[22:0]} : {1'b0, b[22:0]};
    
    // Calculate product (24x24 -> 48-bit) using custom multiplier
    wire [47:0] product;
    multiplier_nbit_full #(.WIDTH(24), .IMPL_TYPE(IMPL_TYPE)) u_multiplier (
        .A(a_significand),
        .B(b_significand),
        .P(product)
    );
    
    // Product round: ending 22 bits are OR'ed for rounding operation
    wire product_round = |product_normalised[22:0];
    
    // Normalization check
    wire is_normalised = product[47];
    wire [47:0] product_normalised = is_normalised ? product : product << 1;

    // Final Mantissa
    // Use adder_nbit_cin for mantissa addition (product_normalised[46:24] + rounding)
    wire [23:0] product_mantissa;
    adder_nbit_cin #(.WIDTH(24)) u_mantissa_adder (
        .A({{1'b0}, {product_normalised[46:24]}}),
        .B({{23'b0}, {(product_normalised[23] & product_round)}}),
        .Cin(1'b0),
        .Sum(product_mantissa)
    );
    wire is_renormalized = product_mantissa[23] ? 1'b1 : 1'b0;

    // Zero detection
    wire is_zero = is_exception ? 1'b0 : (product_normalised[47:24] == 24'd0) ? 1'b1 : 1'b0;
    
    // Sum of exponents
    // Use adder_nbit for summing exponents
    wire [8:0] sum_exponent;
    adder_nbit_cin #(.WIDTH(9)) u_exponent_adder (
        .A({1'b0, a[30:23]}),
        .B({1'b0, b[30:23]}),
        .Cin(1'b0),
        .Sum(sum_exponent)
    );
    
    // Final exponent calculation
    // assign exponent = sum_exponent - 8'd127 + normalised + renormalized; (TODO: delete this)
    // -127 = +9'h181 in two's complement (for 9-bit arithmetic)
    wire [8:0] bias   = 9'h181;
    wire [1:0] k      = { (is_normalised & is_renormalized), (is_normalised ^ is_renormalized) }; // 0..2
    wire [8:0] k_ext  = {7'b0, k};

    // Implement exponent = sum_exponent + bias + k_ext using two adder_nbit_cin instances
    wire [8:0] exponent_tmp1;  // sum_exponent + bias
    wire [8:0] exponent;
    adder_nbit_cin #(.WIDTH(9)) u_exp_bias_adder (
        .A(sum_exponent),
        .B(bias),       // bias is 8 bits, pad to 9
        .Cin(1'b0),
        .Sum(exponent_tmp1)
    );
    adder_nbit_cin #(.WIDTH(9)) u_exp_kext_adder (
        .A(exponent_tmp1),
        .B(k_ext),      // k_ext is 8 bits, pad to 9
        .Cin(1'b0),
        .Sum(exponent)
    );
    
    // Overflow detection: If overall exponent is greater (or equal) to 255 then Overflow condition
    // Note: We need to exclude negative values (0x180-0x1FF) which have bit8=1 but bit7=1
    // Overflow occurs when: (bit8=1 AND bit7=0, meaning >=256) OR (exponent = 255 exactly)
    // Values 0x100-0x17F (256-383) are overflow, values 0x180-0x1FF (384-511, signed: -128 to -1) are underflow
    wire exp_gt_255 = exponent[8] & ~exponent[7];   // >255: bit8=1 AND bit7=0 (values 256-383)
    wire exp_eq_255 = ~exponent[8] & (&exponent[7:0]); // 255: bit8=0, all lower bits=1
    wire is_overflow = !is_zero & (exp_gt_255 | exp_eq_255);
    
    // Underflow detection: If exponent is negative (in two's complement) then Underflow condition
    // Negative values in 9-bit two's complement: 0x180-0x1FF (384-511, represents -128 to -1)
    // These have bit8=1 AND bit7=1
    wire is_underflow = (exponent[8] & exponent[7] & !is_zero) ? 1'b1 : 1'b0;
    
    // Final result - IEEE-754 priority order
    assign result = 
                    is_nan        ? {result_sign, 8'hFF, 23'h400000} :                    // NaN
                    is_overflow   ? {result_sign, 8'hFF, 23'd0} :                // Infinity
                    is_underflow  ? {result_sign, 31'd0} :                        // Zero (underflow)
                    is_zero       ? {result_sign, 31'd0} :                        // Zero (normal)
                    is_exception  ? {result_sign, 8'hFF, 23'd0} :                  // Infinity (inf × inf, inf × normal)
                    {result_sign, exponent[7:0], product_mantissa[22:0]};      // Normal result

endmodule
