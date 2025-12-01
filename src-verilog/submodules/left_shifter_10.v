module left_shifter_10(
    input [9:0] in,
    input [3:0] shift_amt,
    output [9:0] out
);

    // Left shifter implementation using barrel shifter
    wire [9:0] s1 = shift_amt[3] ? {in[1:0], 8'b0} : in;
    wire [9:0] s2 = shift_amt[2] ? {s1[5:0], 4'b0} : s1;
    wire [9:0] s3 = shift_amt[1] ? {s2[7:0], 2'b0} : s2;
    wire [9:0] s4 = shift_amt[0] ? {s3[8:0], 1'b0} : s3;
    assign out = s4;

endmodule
