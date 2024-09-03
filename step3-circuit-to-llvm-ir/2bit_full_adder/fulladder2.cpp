#include <cstdint>

void fullAdder2(
	uint64_t pi0,
	uint64_t pi1,
	uint64_t pi2,
	uint64_t pi3,
	uint64_t pi4,
	uint64_t &po0,
	uint64_t &po1,
	uint64_t &po2
)
{
	uint64_t new_n9, new_n10, new_n11, new_n12, new_n13, new_n14, new_n15, new_n16, new_n17, new_n18, new_n19, new_n21, new_n22, new_n23, new_n24, new_n25, new_n26, new_n27, new_n28, new_n29, new_n30, new_n31, new_n32, new_n33, new_n34, new_n36, new_n37;
	new_n9 = ~pi2;
	new_n10 = ~(new_n9 | pi0);
	new_n11 = ~pi0;
	new_n12 = ~(pi2 | new_n11);
	new_n13 = ~(new_n12 | new_n10);
	new_n14 = ~(new_n13 & pi4);
	new_n15 = ~pi4;
	new_n16 = ~(pi2 & new_n11);
	new_n17 = ~(new_n9 & pi0);
	new_n18 = ~(new_n17 & new_n16);
	new_n19 = ~(new_n18 & new_n15);
	po0 = ~(new_n19 & new_n14);
	new_n21 = ~(new_n9 | new_n11);
	new_n22 = ~new_n21;
	new_n23 = ~(new_n18 & pi4);
	new_n24 = ~(new_n23 & new_n22);
	new_n25 = ~pi3;
	new_n26 = ~(new_n25 | pi1);
	new_n27 = ~(new_n25 & pi1);
	new_n28 = ~new_n27;
	new_n29 = ~(new_n28 | new_n26);
	new_n30 = ~(new_n29 & new_n24);
	new_n31 = ~(new_n13 | new_n15);
	new_n32 = ~(new_n31 | new_n21);
	new_n33 = ~new_n29;
	new_n34 = ~(new_n33 & new_n32);
	po1 = ~(new_n34 & new_n30);
	new_n36 = ~(pi3 & pi1);
	new_n37 = ~(new_n33 & new_n24);
	po2 = ~(new_n37 & new_n36);

}
