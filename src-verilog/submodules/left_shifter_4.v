module left_shifter_4(
    input [3:0] in,
    input [2:0] shift_amt,
    output [3:0] out
);

    // Left shifter implementation using barrel shifter
    wire [3:0] s0 = shift_amt[2] ? {4'b0} : in;
    wire [3:0] s1 = shift_amt[1] ? {s0[1:0], 2'b0} : s0;
    wire [3:0] s2 = shift_amt[0] ? {s1[2:0], 1'b0} : s1;
    assign out = s2;

endmodule
