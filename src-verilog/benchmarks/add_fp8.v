module add_fp8
#(
    parameter IMPL_TYPE = 0
)
(
    input [7:0] a,
    input [7:0] b,
    output [7:0] result
);
    // Step 0: Special cases
    
    // Infinity flag sets 1 if either one of the exponent is 255
    wire a_is_infinity = (&a[6:4]);
    wire b_is_infinity = (&b[6:4]);
    wire is_infinity = a_is_infinity | b_is_infinity;

    wire a_is_zero = ~|a[6:4] & ~|a[3:0];
    wire b_is_zero = ~|b[6:4] & ~|b[3:0];
    wire is_zero = a_is_zero & b_is_zero;
   

    // nan detection: NaN occurs when either operand is NaN (exp=255 with non-zero mantissa)
    wire a_is_nan = (&a[6:4]) & (|a[3:0]);
    wire b_is_nan = (&b[6:4]) & (|b[3:0]);
    wire is_nan = a_is_nan | b_is_nan | (a_is_infinity & b_is_infinity & (a_sign ^ b_sign));

    // Step 1: Extract sign, exponent, and mantissa from inputs
    wire a_sign = a[7];
    wire b_sign = b[7];
    wire [2:0] a_exp = a[6:4];
    wire [2:0] b_exp = b[6:4];
    wire [3:0] a_mantissa = a[3:0];
    wire [3:0] b_mantissa = b[3:0];
    
    // Add hidden bit for normalized numbers
    wire [4:0] a_mantissa_5 = (a_is_zero) ? {1'b0, a_mantissa} : {1'b1, a_mantissa};
    wire [4:0] b_mantissa_5 = (b_is_zero) ? {1'b0, b_mantissa} : {1'b1, b_mantissa};
    
    
    // Step 2: Compute the difference in exponents  
    wire [2:0] exp_diff; 
    adder_nbit_cin #(.WIDTH(3), .IMPL_TYPE(IMPL_TYPE)) u_exp_diff_adder (
        .A(a_exp),
        .B(~b_exp),
        .Cin(1'b1),
        .Sum(exp_diff)
    );
    wire swap_exp = exp_diff[2];
    wire [2:0] larger_exp = swap_exp ? b_exp : a_exp;
    wire [4:0] larger_mantissa = swap_exp ? b_mantissa_5 : a_mantissa_5;
    wire [4:0] smaller_mantissa = swap_exp ? a_mantissa_5 : b_mantissa_5;
    wire larger_sign = swap_exp ? b_sign : a_sign;

    wire [2:0] exp_diff_second_operand = (exp_diff[2]) ? ~exp_diff : exp_diff;
    wire exp_diff_carry_in = (exp_diff[2]) ? 1'b1 : 1'b0;
    // use adder_nbit_cin to add the larger_exp and the exp_diff_second_operand
    wire [2:0] exp_diff_abs;
    adder_nbit_cin #(.WIDTH(3), .IMPL_TYPE(IMPL_TYPE)) u_exp_diff_abs_adder (
        .A(3'b0),
        .B(exp_diff_second_operand),
        .Cin(exp_diff_carry_in),
        .Sum(exp_diff_abs)
    );

    // Step 3: Shift the smaller mantissa by the difference in exponents
    wire [4:0] smaller_mantissa_shifted;
    right_shifter_5 right_shifter_inst (
        .in(smaller_mantissa),
        .shift_amt(exp_diff_abs[2:0]),
        .upper_exp_bits(3'b0),
        .out(smaller_mantissa_shifted)
    );

    // Step 4: Determine the effective operation
    wire operation_add = a_sign == b_sign;

    // Step 5: Perform the addition/subtraction
    wire [5:0] smaller_mantissa_shifted_and_extended = operation_add ? ({1'b0, smaller_mantissa_shifted}) : ({smaller_mantissa_shifted[4], smaller_mantissa_shifted});
    wire [5:0] mantissa_sub_add_result;
    adder_nbit_cin #(.WIDTH(6), .IMPL_TYPE(IMPL_TYPE)) u_M_result_adder (
        .A({1'b0, larger_mantissa}),
        .B((~operation_add) ? (~smaller_mantissa_shifted_and_extended) : smaller_mantissa_shifted_and_extended),
        .Cin(~operation_add),
        .Sum(mantissa_sub_add_result)
    );

    // Step 6: Normalize the result
    // find the position of the leading 1 in the M_sub_add_result[4:0] and shift the result left by the position
    wire [2:0] leading_1_position_tmp, leading_1_position;
    leading_one_detector_8 leading_one_detector_inst (
        .x({3'b0, mantissa_sub_add_result[4:0]}),
        .n(leading_1_position_tmp)
    );
    assign leading_1_position = (leading_1_position_tmp == 3'd7) ? 3'd0 : (leading_1_position_tmp - 3'd3);

    wire [3:0] mantissa_sub_normalized_shifted;
    left_shifter_4 left_shifter_inst (
        .in(mantissa_sub_add_result[3:0]),
        .shift_amt(leading_1_position),
        .out(mantissa_sub_normalized_shifted)
    );

    wire do_right_shift = mantissa_sub_add_result[5] ? 1'b1 : 1'b0;    
    wire [3:0] mantissa_add_normalized = do_right_shift ? mantissa_sub_add_result[4:1] : mantissa_sub_add_result[3:0];
    wire [3:0] result_mantissa = operation_add ? mantissa_add_normalized : mantissa_sub_normalized_shifted[3:0];

    // Step 7: Calculate the exponent
    // Exponent arithmetic using adder_nbit_cin and a mux for selecting add/sub
    wire [2:0] second_operand = operation_add ? {2'b0, do_right_shift} : ~leading_1_position;
    wire carry_in = operation_add ? 1'b0 : 1'b1;
    wire [2:0] result_exp;
    adder_nbit_cin #(.WIDTH(3), .IMPL_TYPE(IMPL_TYPE)) u_exp_add (
        .A(larger_exp),
        .B(second_operand),
        .Cin(carry_in),
        .Sum(result_exp)
    );

    // Step 8: Compute the sign
    wire result_sign = operation_add ? a_sign : (larger_sign ^ mantissa_sub_add_result[5]);

    // Step 9: Handle overflow and underflow
    wire overflow = (result_exp == 3'd7);
    wire underflow = (result_exp == 3'd0 | (mantissa_sub_add_result[5] & ~operation_add));

    assign result = 
                    is_nan        ? {1'b0, 3'h7, 4'h8} :                    // NaN
                    is_infinity   ? {(a_is_infinity ? a_sign : b_sign), 3'h7, 4'h0} :                  // Infinity
                    is_zero       ? {result_sign, 3'h0, 4'h0} :                  // Zero
                    overflow   ? {result_sign, 3'h7, 4'h0} :                  // Infinity
                    underflow  ? {result_sign, 3'h0, 4'h0} :                  // gradual underflow
                    {result_sign, result_exp, result_mantissa};                  // Normal result
  
endmodule

