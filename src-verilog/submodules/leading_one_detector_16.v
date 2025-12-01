/* verilator lint_off DECLFILENAME */
/* verilator lint_off UNUSEDSIGNAL */

module leading_one_detector_16 (
    input  [15:0] x,
    output [3:0]  n
);
    // Shared zero checks (reused across data/accumulator paths)
    wire z_in   = (x == 16'b0);

    wire z8     = ~|x[15:8]; // checks x[15:8] == 0
    wire [15:0] x8  = z8  ? (x << 8) : x;

    wire z4     = ~|x8[15:12];  // checks x8[15:12] == 0
    wire [15:0] x4  = z4  ? (x8 << 4) : x8;

    wire z2     = ~|x4[15:14];  // checks x4[15:14] == 0
    wire [15:0] x2  = z2  ? (x4 << 2) : x4;

    wire z1     = ~x2[15];      // checks x2[15] == 0

    // Partial results (bit-setting equivalent to n |= (1 << i))
    wire [3:0] a8  = z8  ? 4'd8  : 4'd0;
    wire [3:0] a4  = z4  ? 4'd4  : 4'd0;
    wire [3:0] a2  = z2  ? 4'd2  : 4'd0;
    wire [3:0] a1  = z1  ? 4'd1  : 4'd0;

    // Final count (sum via OR since bits are non-overlapping)
    assign n = z_in ? 4'd15 : (a8 | a4 | a2 | a1);
endmodule
