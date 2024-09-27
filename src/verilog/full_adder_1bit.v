// 1-bit full adder
// deyuan, 08/20/2024

module full_adder_1bit (pi0, pi1, pi2, po0, po1);

input pi0;
input pi1;
input pi2;
output po0;
output po1;

assign po0 = (pi0 ^ pi1 ^ pi2);
assign po1 = ((pi0 & pi1) | (pi2 & (pio0 ^ pi1)));

endmodule

