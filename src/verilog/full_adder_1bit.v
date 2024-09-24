// 1-bit full adder

module full_adder_1bit (a, b, cin, sum, cout);

input a;
input b;
input cin;
output sum;
output cout;

assign sum = (a ^ b ^ cin);
assign cout = ((a & b) | (cin & (a ^ b)));

endmodule

