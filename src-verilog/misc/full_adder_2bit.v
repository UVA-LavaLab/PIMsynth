// 2-bit full adder
// hosein, 09/03/2024

module full_adder_2bit (
    a, b, cin, sum, cout
);

    // Declare inputs and outputs inside the module
    input [1:0] a;
    input [1:0] b;
    input cin;
    output [1:0] sum;
    output cout;

    // Internal wires
    wire carry1, carry2;

    // First bit computation
    assign sum[0] = a[0] ^ b[0] ^ cin;
    assign carry1 = (a[0] & b[0]) | (cin & (a[0] ^ b[0]));

    // Second bit computation
    assign sum[1] = a[1] ^ b[1] ^ carry1;
    assign carry2 = (a[1] & b[1]) | (carry1 & (a[1] ^ b[1]));

    // Final carry out
    assign cout = carry2;

endmodule

