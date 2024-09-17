	.text
	.attribute	4, 16
	.attribute	5, "rv32i2p1_m2p0_a2p1_c2p0_zmmul1p0"
	.file	"fulladder2.c"
	.globl	fullAdder2                      # -- Begin function fullAdder2
	.p2align	1
	.type	fullAdder2,@function
fullAdder2:                             # @fullAdder2
# %bb.0:
	addi	sp, sp, -96
	sw	ra, 92(sp)                      # 4-byte Folded Spill
	sw	s0, 88(sp)                      # 4-byte Folded Spill
	sw	s1, 84(sp)                      # 4-byte Folded Spill
	sw	s2, 80(sp)                      # 4-byte Folded Spill
	sw	s3, 76(sp)                      # 4-byte Folded Spill
	sw	s4, 72(sp)                      # 4-byte Folded Spill
	sw	s5, 68(sp)                      # 4-byte Folded Spill
	sw	s6, 64(sp)                      # 4-byte Folded Spill
	sw	s7, 60(sp)                      # 4-byte Folded Spill
	sw	s8, 56(sp)                      # 4-byte Folded Spill
	sw	s9, 52(sp)                      # 4-byte Folded Spill
	sw	s10, 48(sp)                     # 4-byte Folded Spill
	sw	s11, 44(sp)                     # 4-byte Folded Spill
	sw	a7, 36(sp)                      # 4-byte Folded Spill
	sw	a6, 32(sp)                      # 4-byte Folded Spill
	sw	a5, 28(sp)                      # 4-byte Folded Spill
	lw	t0, 0(a0)
	sw	t0, 40(sp)                      # 4-byte Folded Spill
	lw	a0, 0(a1)
	sw	a0, 20(sp)                      # 4-byte Folded Spill
	lw	t1, 0(a2)
	lw	t3, 0(a4)
	lw	a0, 0(a3)
	sw	a0, 16(sp)                      # 4-byte Folded Spill
	#APP
	########## BEGIN ##########
	#NO_APP
	#APP
	xor	t0, t1, t0
	not	t0, t0
	#NO_APP
	#APP
	xor	t2, t0, t3
	not	t2, t2
	#NO_APP
	sw	t2, 24(sp)                      # 4-byte Folded Spill
	lw	t2, 40(sp)                      # 4-byte Folded Reload
	#APP
	and	t1, t1, t2
	#NO_APP
	#APP
	not	t1, t1
	#NO_APP
	#APP
	not	t0, t0
	#NO_APP
	#APP
	and	t0, t0, t3
	#NO_APP
	#APP
	not	t0, t0
	#NO_APP
	#APP
	and	t0, t0, t1
	#NO_APP
	#APP
	not	t0, t0
	#NO_APP
	sw	t0, 40(sp)                      # 4-byte Folded Spill
	lw	t3, 20(sp)                      # 4-byte Folded Reload
	lw	t2, 16(sp)                      # 4-byte Folded Reload
	#APP
	xor	t1, t2, t3
	not	t1, t1
	#NO_APP
	lw	t0, 40(sp)                      # 4-byte Folded Reload
	#APP
	xor	t0, t1, t0
	not	t0, t0
	#NO_APP
	sw	t0, 12(sp)                      # 4-byte Folded Spill
	#APP
	and	t3, t2, t3
	#NO_APP
	#APP
	not	t3, t3
	#NO_APP
	#APP
	not	t1, t1
	#NO_APP
	lw	t0, 40(sp)                      # 4-byte Folded Reload
	#APP
	and	t0, t1, t0
	#NO_APP
	#APP
	not	t0, t0
	#NO_APP
	#APP
	and	t0, t0, t3
	#NO_APP
	#APP
	########## END ##########
	#NO_APP
	lw	a0, 28(sp)                      # 4-byte Folded Reload
	lw	a1, 24(sp)                      # 4-byte Folded Reload
	sw	a1, 0(a0)
	lw	a0, 32(sp)                      # 4-byte Folded Reload
	lw	a1, 12(sp)                      # 4-byte Folded Reload
	sw	a1, 0(a0)
	#APP
	not	t0, t0
	#NO_APP
	lw	a0, 36(sp)                      # 4-byte Folded Reload
	sw	t0, 0(a0)
	lw	ra, 92(sp)                      # 4-byte Folded Reload
	lw	s0, 88(sp)                      # 4-byte Folded Reload
	lw	s1, 84(sp)                      # 4-byte Folded Reload
	lw	s2, 80(sp)                      # 4-byte Folded Reload
	lw	s3, 76(sp)                      # 4-byte Folded Reload
	lw	s4, 72(sp)                      # 4-byte Folded Reload
	lw	s5, 68(sp)                      # 4-byte Folded Reload
	lw	s6, 64(sp)                      # 4-byte Folded Reload
	lw	s7, 60(sp)                      # 4-byte Folded Reload
	lw	s8, 56(sp)                      # 4-byte Folded Reload
	lw	s9, 52(sp)                      # 4-byte Folded Reload
	lw	s10, 48(sp)                     # 4-byte Folded Reload
	lw	s11, 44(sp)                     # 4-byte Folded Reload
	addi	sp, sp, 96
	ret
.Lfunc_end0:
	.size	fullAdder2, .Lfunc_end0-fullAdder2
                                        # -- End function
	.ident	"clang version 20.0.0git (https://github.com/llvm/llvm-project.git d550ada5ab6cd6e49de71ac4c9aa27ced4c11de0)"
	.section	".note.GNU-stack","",@progbits
	.addrsig
