	.text
	.attribute	4, 16
	.attribute	5, "rv32i2p1_m2p0_a2p1_c2p0_zmmul1p0"
	.file	"fulladder1.c"
	.globl	fullAdder1                      # -- Begin function fullAdder1
	.p2align	1
	.type	fullAdder1,@function
fullAdder1:                             # @fullAdder1
# %bb.0:
	addi	sp, sp, -80
	sw	ra, 76(sp)                      # 4-byte Folded Spill
	sw	s0, 72(sp)                      # 4-byte Folded Spill
	sw	s1, 68(sp)                      # 4-byte Folded Spill
	sw	s2, 64(sp)                      # 4-byte Folded Spill
	sw	s3, 60(sp)                      # 4-byte Folded Spill
	sw	s4, 56(sp)                      # 4-byte Folded Spill
	sw	s5, 52(sp)                      # 4-byte Folded Spill
	sw	s6, 48(sp)                      # 4-byte Folded Spill
	sw	s7, 44(sp)                      # 4-byte Folded Spill
	sw	s8, 40(sp)                      # 4-byte Folded Spill
	sw	s9, 36(sp)                      # 4-byte Folded Spill
	sw	s10, 32(sp)                     # 4-byte Folded Spill
	sw	s11, 28(sp)                     # 4-byte Folded Spill
	lw	t0, 0(a0)
	sw	t0, 8(sp)                       # 4-byte Folded Spill
	lw	t3, 0(a1)
	lw	t2, 0(a2)
	sw	t2, 12(sp)                      # 4-byte Folded Spill
	sw	a4, 24(sp)                      # 4-byte Folded Spill
	sw	a3, 20(sp)                      # 4-byte Folded Spill
	#APP
	########## BEGIN ##########
	#NO_APP
	#APP
	xor	t1, t3, t0
	not	t1, t1
	#NO_APP
	#APP
	xor	t0, t1, t2
	not	t0, t0
	#NO_APP
	sw	t0, 16(sp)                      # 4-byte Folded Spill
	lw	t0, 8(sp)                       # 4-byte Folded Reload
	#APP
	and	t2, t3, t0
	#NO_APP
	#APP
	not	t2, t2
	#NO_APP
	#APP
	not	t1, t1
	#NO_APP
	lw	t0, 12(sp)                      # 4-byte Folded Reload
	#APP
	and	t0, t1, t0
	#NO_APP
	#APP
	not	t0, t0
	#NO_APP
	#APP
	and	t0, t0, t2
	#NO_APP
	#APP
	########## END ##########
	#NO_APP
	lw	a0, 20(sp)                      # 4-byte Folded Reload
	lw	a1, 16(sp)                      # 4-byte Folded Reload
	sw	a1, 0(a0)
	#APP
	not	t0, t0
	#NO_APP
	lw	a0, 24(sp)                      # 4-byte Folded Reload
	sw	t0, 0(a0)
	lw	ra, 76(sp)                      # 4-byte Folded Reload
	lw	s0, 72(sp)                      # 4-byte Folded Reload
	lw	s1, 68(sp)                      # 4-byte Folded Reload
	lw	s2, 64(sp)                      # 4-byte Folded Reload
	lw	s3, 60(sp)                      # 4-byte Folded Reload
	lw	s4, 56(sp)                      # 4-byte Folded Reload
	lw	s5, 52(sp)                      # 4-byte Folded Reload
	lw	s6, 48(sp)                      # 4-byte Folded Reload
	lw	s7, 44(sp)                      # 4-byte Folded Reload
	lw	s8, 40(sp)                      # 4-byte Folded Reload
	lw	s9, 36(sp)                      # 4-byte Folded Reload
	lw	s10, 32(sp)                     # 4-byte Folded Reload
	lw	s11, 28(sp)                     # 4-byte Folded Reload
	addi	sp, sp, 80
	ret
.Lfunc_end0:
	.size	fullAdder1, .Lfunc_end0-fullAdder1
                                        # -- End function
	.ident	"clang version 20.0.0git (https://github.com/llvm/llvm-project.git d550ada5ab6cd6e49de71ac4c9aa27ced4c11de0)"
	.section	".note.GNU-stack","",@progbits
	.addrsig
