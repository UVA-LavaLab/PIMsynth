// fp32 mul 
// hosein, 11/21/2024

module FloatingPointMultiplier (
    input [31:0] a,    // Input operand 1
    input [31:0] b,    // Input operand 2
    output [31:0] result // Output result
);
    // Split the inputs into sign, exponent, and mantissa
    wire sign_a, sign_b, sign_result;
    wire [7:0] exponent_a, exponent_b, temp_exponent, exponent_result;
    wire [23:0] mantissa_a, mantissa_b;
    wire [47:0] mantissa_product;
    wire [22:0] mantissa_result;

    assign sign_a = a[31];
    assign sign_b = b[31];
    assign exponent_a = a[30:23];
    assign exponent_b = b[30:23];
    assign mantissa_a = {1'b1, a[22:0]}; // Add implicit 1 for normalized numbers
    assign mantissa_b = {1'b1, b[22:0]}; // Add implicit 1 for normalized numbers

    // Calculate the sign of the result
    assign sign_result = sign_a ^ sign_b;

    // Exponent calculation (subtract bias of 127 and add exponents)
    assign temp_exponent = exponent_a + exponent_b - 127;

    // Multiply mantissas (24-bit * 24-bit gives a 48-bit product)
    assign mantissa_product = mantissa_a * mantissa_b;

    // Normalize the result
    wire mantissa_msb = mantissa_product[47];
    assign mantissa_result = mantissa_msb ? mantissa_product[46:24] : mantissa_product[45:23];
    assign exponent_result = mantissa_msb ? temp_exponent + 1 : temp_exponent;

    // Handle special cases: zero, infinity, NaN, overflow, and underflow
    wire is_zero_a, is_zero_b, is_infinity_a, is_infinity_b, is_nan_a, is_nan_b;
    wire [31:0] special_result;

    assign is_zero_a = (a[30:0] == 0);
    assign is_zero_b = (b[30:0] == 0);
    assign is_infinity_a = (exponent_a == 8'hFF && a[22:0] == 0);
    assign is_infinity_b = (exponent_b == 8'hFF && b[22:0] == 0);
    assign is_nan_a = (exponent_a == 8'hFF && a[22:0] != 0);
    assign is_nan_b = (exponent_b == 8'hFF && b[22:0] != 0);

    assign special_result = 
        (is_nan_a || is_nan_b) ? {1'b0, 8'hFF, 1'b1, 22'b0} : // NaN
        (is_infinity_a || is_infinity_b) ? 
            ((is_zero_a || is_zero_b) ? {1'b0, 8'hFF, 1'b1, 22'b0} : {sign_result, 8'hFF, 23'b0}) : // Infinity or NaN
        (is_zero_a || is_zero_b) ? 32'b0 : // Zero
        (temp_exponent[8]) ? 32'b0 : // Underflow
        (temp_exponent > 254) ? {sign_result, 8'hFF, 23'b0} : // Overflow
        {sign_result, exponent_result[7:0], mantissa_result}; // Normal case

    assign result = special_result;

endmodule

