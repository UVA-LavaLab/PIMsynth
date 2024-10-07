// 1-bit full adder
// deyuan, 08/20/2024

module full_adder_1bit (a, b, cin, sum, cout);

input a;
input b;
input cin;
output sum;
output cout;

assign sum = (a ^ b ^ cin);
assign cout = ((a & b) | (cin & (a ^ b)));

endmodule

