// 2-bit full adder
// hosein, 09/03/2024

module full_adder_2bit (
    pi0, pi1, pi2, po0, po1
);

    // Declare inputs and outputs inside the module
    input [1:0] pi0;
    input [1:0] pi1;
    input pi2;
    output [1:0] po0;
    output po1;

    // Internal wires
    wire carry1, carry2;

    // First bit computation
    assign po0[0] = pi0[0] ^ pi1[0] ^ pi2;
    assign carry1 = (pi0[0] & pi1[0]) | (pi2 & (pi0[0] ^ pi1[0]));

    // Second bit computation
    assign po0[1] = pi0[1] ^ pi1[1] ^ carry1;
    assign carry2 = (pi0[1] & pi1[1]) | (carry1 & (pi0[1] ^ pi1[1]));

    // Final carry out
    assign po1 = carry2;

endmodule

