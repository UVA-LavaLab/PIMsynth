module right_shifter_11(
    input [10:0] in,
    input [4:0] shift_amt,
    input [4:0] upper_exp_bits,
    output [10:0] out
);
   // Right shifter implementation using barrel shifter
    wire [10:0] s0 = shift_amt[4] ? { 11'b0} : in;
    wire [10:0] s1 = shift_amt[3] ? { 8'b0,  s0[10: 8]} : s0;
    wire [10:0] s2 = shift_amt[2] ? { 4'b0,  s1[10: 4]} : s1;
    wire [10:0] s3 = shift_amt[1] ? { 2'b0,  s2[10: 2]} : s2;
    wire [10:0] s4 = shift_amt[0] ? { 1'b0,  s3[10: 1]} : s3;
    assign out = (|upper_exp_bits) ? 11'b0 : s4;
endmodule
