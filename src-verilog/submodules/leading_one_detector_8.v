/* verilator lint_off DECLFILENAME */
/* verilator lint_off UNUSEDSIGNAL */

module leading_one_detector_8 (
    input  [7:0] x,
    output [2:0]  n
);

    wire z_in   = (x == 8'b0);
    wire z4     = ~|x[7:4];  // checks x[7:4] == 0
    wire [7:0] x4  = z4  ? (x << 4) : x;

    wire z2     = ~|x4[7:6];  // checks x4[7:6] == 0
    wire [7:0] x2  = z2  ? (x4 << 2) : x4;

    wire z1     = ~x2[7];      // checks x2[7] == 0

    // Partial results (bit-setting equivalent to n |= (1 << i))
    wire [2:0] a4  = z4  ? 3'd4  : 3'd0;
    wire [2:0] a2  = z2  ? 3'd2  : 3'd0;
    wire [2:0] a1  = z1  ? 3'd1  : 3'd0;

    // Final count (sum via OR since bits are non-overlapping)
    assign n = z_in ? 3'd7 : (a4 | a2 | a1);
endmodule
