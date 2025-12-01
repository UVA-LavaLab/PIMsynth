module right_shifter_5(
    input [4:0] in,
    input [2:0] shift_amt,
    input [2:0] upper_exp_bits,
    output [4:0] out
);

    // Right shifter implementation using barrel shifter
    wire [4:0] s0 = shift_amt[2] ? {4'b0, in[4]} : in; 
    wire [4:0] s1 = shift_amt[1] ? {3'b0, s0[4: 3]} : s0;
    wire [4:0] s2 = shift_amt[0] ? {1'b0, s1[4: 1]} : s1;
    assign out = (|upper_exp_bits) ? 5'b0 : s2;
endmodule
