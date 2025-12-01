module left_shifter_23(
    input [22:0] in,
    input [4:0] shift_amt,
    output [22:0] out
);

    // Left shifter implementation using barrel shifter
    wire [22:0] s0 = shift_amt[4] ? {in[6:0], 16'b0} : in;
    wire [22:0] s1 = shift_amt[3] ? {s0[14:0], 8'b0} : s0;
    wire [22:0] s2 = shift_amt[2] ? {s1[18:0], 4'b0} : s1;
    wire [22:0] s3 = shift_amt[1] ? {s2[20:0], 2'b0} : s2;
    wire [22:0] s4 = shift_amt[0] ? {s3[21:0], 1'b0} : s3;
    assign out = s4;

endmodule
