/* verilator lint_off DECLFILENAME */
/* verilator lint_off UNUSEDSIGNAL */

module leading_one_detector_32 (
    input  [31:0] x,
    output [4:0]  n
);
    // Shared zero checks (reused across data/accumulator paths)
    wire z_in   = (x == 32'b0);
    wire z16    = ~|x[31:16];   // checks x[31:16] == 0
    wire [31:0] x16 = z16 ? (x << 16) : x;

    wire z8     = ~|x16[31:24]; // checks x16[31:24] == 0
    wire [31:0] x8  = z8  ? (x16 << 8) : x16;

    wire z4     = ~|x8[31:28];  // checks x8[31:28] == 0
    wire [31:0] x4  = z4  ? (x8 << 4) : x8;

    wire z2     = ~|x4[31:30];  // checks x4[31:30] == 0
    wire [31:0] x2  = z2  ? (x4 << 2) : x4;

    wire z1     = ~x2[31];      // checks x2[31] == 0

    // Partial results (bit-setting equivalent to n |= (1 << i))
    wire [4:0] a16 = z16 ? 5'd16 : 5'd0;
    wire [4:0] a8  = z8  ? 5'd8  : 5'd0;
    wire [4:0] a4  = z4  ? 5'd4  : 5'd0;
    wire [4:0] a2  = z2  ? 5'd2  : 5'd0;
    wire [4:0] a1  = z1  ? 5'd1  : 5'd0;

    // Final count (sum via OR since bits are non-overlapping)
    assign n = z_in ? 5'd31 : (a16 | a8 | a4 | a2 | a1);
endmodule
