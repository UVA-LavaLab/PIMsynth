// 1-bit full adder

module 1bit_full_adder (a, b, cin, sum, cout);

input a;
input b;
input cin;
output sum;
output cout;

assign sum = (a ^ b ^ cin);
assign cout = ((a & b) | (cin & (a ^ b)));

endmodule

