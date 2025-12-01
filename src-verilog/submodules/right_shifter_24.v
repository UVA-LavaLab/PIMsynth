module right_shifter_24(
    input [23:0] in,
    input [4:0] shift_amt,
    input [2:0] upper_exp_bits,
    output [23:0] out
);

    // Right shifter implementation using barrel shifter
    wire [23:0] s0 = shift_amt[4] ? {16'b0, in[23:16]} : in;
    wire [23:0] s1 = shift_amt[3] ? { 8'b0,  s0[23: 8]} : s0;
    wire [23:0] s2 = shift_amt[2] ? { 4'b0,  s1[23: 4]} : s1;
    wire [23:0] s3 = shift_amt[1] ? { 2'b0,  s2[23: 2]} : s2;
    wire [23:0] s4 = shift_amt[0] ? { 1'b0,  s3[23: 1]} : s3;
    assign out = (|upper_exp_bits) ? 24'b0 : s4;

endmodule
