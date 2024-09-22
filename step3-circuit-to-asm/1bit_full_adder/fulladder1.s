	.text
	.attribute	4, 16
	.attribute	5, "rv32i2p1_m2p0_a2p1_c2p0_zmmul1p0"
	.file	"fulladder1.c"
	.globl	fullAdder1                      # -- Begin function fullAdder1
	.p2align	1
	.type	fullAdder1,@function
fullAdder1:                             # @fullAdder1
.Lfunc_begin0:
	.file	0 "/u/uab9qt/worktable/llvm_repos/bit-serial-compiler/step3-circuit-to-asm/1bit_full_adder" "fulladder1.c" md5 0xb38f70c24d434d8a2a7c79f5a0ae8895
	.loc	0 13 0                          # fulladder1.c:13:0
	.cfi_sections .debug_frame
	.cfi_startproc
# %bb.0:
	#DEBUG_VALUE: fullAdder1:pi0_p <- $x10
	#DEBUG_VALUE: fullAdder1:pi1_p <- $x11
	#DEBUG_VALUE: fullAdder1:pi2_p <- $x12
	#DEBUG_VALUE: fullAdder1:pi3_p <- $x13
	#DEBUG_VALUE: fullAdder1:pi4_p <- $x14
	#DEBUG_VALUE: fullAdder1:po0_p <- $x15
	#DEBUG_VALUE: fullAdder1:po1_p <- $x16
	#DEBUG_VALUE: fullAdder1:po2_p <- $x17
	addi	sp, sp, -96
	.cfi_def_cfa_offset 96
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
	.cfi_offset ra, -4
	.cfi_offset s0, -8
	.cfi_offset s1, -12
	.cfi_offset s2, -16
	.cfi_offset s3, -20
	.cfi_offset s4, -24
	.cfi_offset s5, -28
	.cfi_offset s6, -32
	.cfi_offset s7, -36
	.cfi_offset s8, -40
	.cfi_offset s9, -44
	.cfi_offset s10, -48
	.cfi_offset s11, -52
	sw	a7, 36(sp)                      # 4-byte Folded Spill
.Ltmp0:
	#DEBUG_VALUE: fullAdder1:po2_p <- [DW_OP_plus_uconst 36] [$x2+0]
	sw	a6, 32(sp)                      # 4-byte Folded Spill
.Ltmp1:
	#DEBUG_VALUE: fullAdder1:po1_p <- [DW_OP_plus_uconst 32] [$x2+0]
	sw	a5, 28(sp)                      # 4-byte Folded Spill
.Ltmp2:
	#DEBUG_VALUE: fullAdder1:po0_p <- [DW_OP_plus_uconst 28] [$x2+0]
	.loc	0 15 10 prologue_end            # fulladder1.c:15:10
	lw	t0, 0(a0)
.Ltmp3:
	#DEBUG_VALUE: fullAdder1:pi0 <- $x5
	.loc	0 0 10 is_stmt 0                # fulladder1.c:0:10
	sw	t0, 40(sp)                      # 4-byte Folded Spill
	.loc	0 15 22                         # fulladder1.c:15:22
	lw	a0, 0(a1)
.Ltmp4:
	#DEBUG_VALUE: fullAdder1:pi1 <- $x10
	.loc	0 0 22                          # fulladder1.c:0:22
	sw	a0, 20(sp)                      # 4-byte Folded Spill
.Ltmp5:
	#DEBUG_VALUE: fullAdder1:pi1 <- [DW_OP_plus_uconst 20] [$x2+0]
	#DEBUG_VALUE: fullAdder1:pi1 <- [DW_OP_plus_uconst 20] [$x2+0]
	.loc	0 15 34                         # fulladder1.c:15:34
	lw	t1, 0(a2)
.Ltmp6:
	#DEBUG_VALUE: fullAdder1:pi2 <- $x6
	.loc	0 15 58                         # fulladder1.c:15:58
	lw	t3, 0(a4)
.Ltmp7:
	#DEBUG_VALUE: fullAdder1:pi4 <- $x28
	.loc	0 15 46                         # fulladder1.c:15:46
	lw	a0, 0(a3)
.Ltmp8:
	#DEBUG_VALUE: fullAdder1:pi3 <- $x10
	.loc	0 0 46                          # fulladder1.c:0:46
	sw	a0, 16(sp)                      # 4-byte Folded Spill
.Ltmp9:
	#DEBUG_VALUE: fullAdder1:pi3 <- [DW_OP_plus_uconst 16] [$x2+0]
	#DEBUG_VALUE: fullAdder1:pi3 <- [DW_OP_plus_uconst 16] [$x2+0]
	.loc	0 18 2 is_stmt 1                # fulladder1.c:18:2
	#APP
	########## BEGIN ##########
	#NO_APP
	.loc	0 19 2                          # fulladder1.c:19:2
	#APP
	xor	t0, t1, t0
	not	t0, t0
	#NO_APP
.Ltmp10:
	#DEBUG_VALUE: fullAdder1:new_n9 <- $x5
	#DEBUG_VALUE: fullAdder1:pi0 <- [DW_OP_plus_uconst 40] [$x2+0]
	#DEBUG_VALUE: fullAdder1:pi0 <- $x5
	.loc	0 20 2                          # fulladder1.c:20:2
	#APP
	xor	t2, t0, t3
	not	t2, t2
	#NO_APP
.Ltmp11:
	#DEBUG_VALUE: fullAdder1:po0 <- $x7
	.loc	0 0 2 is_stmt 0                 # fulladder1.c:0:2
	sw	t2, 24(sp)                      # 4-byte Folded Spill
.Ltmp12:
	#DEBUG_VALUE: fullAdder1:po0 <- [DW_OP_plus_uconst 24] [$x2+0]
	#DEBUG_VALUE: fullAdder1:po0 <- [DW_OP_plus_uconst 24] [$x2+0]
	lw	t2, 40(sp)                      # 4-byte Folded Reload
.Ltmp13:
	#DEBUG_VALUE: fullAdder1:pi0 <- $x7
	.loc	0 21 2 is_stmt 1                # fulladder1.c:21:2
	#APP
	and	t1, t1, t2
	#NO_APP
.Ltmp14:
	#DEBUG_VALUE: fullAdder1:new_n11 <- $x6
	.loc	0 22 2                          # fulladder1.c:22:2
	#APP
	not	t1, t1
	#NO_APP
.Ltmp15:
	#DEBUG_VALUE: fullAdder1:new_n12 <- $x6
	.loc	0 23 2                          # fulladder1.c:23:2
	#APP
	not	t0, t0
	#NO_APP
.Ltmp16:
	#DEBUG_VALUE: fullAdder1:new_n13 <- $x5
	.loc	0 24 2                          # fulladder1.c:24:2
	#APP
	and	t0, t0, t3
	#NO_APP
.Ltmp17:
	#DEBUG_VALUE: fullAdder1:new_n14 <- $x5
	.loc	0 25 2                          # fulladder1.c:25:2
	#APP
	not	t0, t0
	#NO_APP
.Ltmp18:
	#DEBUG_VALUE: fullAdder1:new_n15 <- $x5
	.loc	0 26 2                          # fulladder1.c:26:2
	#APP
	and	t0, t0, t1
	#NO_APP
.Ltmp19:
	#DEBUG_VALUE: fullAdder1:new_n16 <- $x5
	.loc	0 27 2                          # fulladder1.c:27:2
	#APP
	not	t0, t0
	#NO_APP
.Ltmp20:
	#DEBUG_VALUE: fullAdder1:new_n17 <- $x5
	.loc	0 0 2 is_stmt 0                 # fulladder1.c:0:2
	sw	t0, 40(sp)                      # 4-byte Folded Spill
.Ltmp21:
	#DEBUG_VALUE: fullAdder1:new_n17 <- [DW_OP_plus_uconst 40] [$x2+0]
	#DEBUG_VALUE: fullAdder1:new_n17 <- [DW_OP_plus_uconst 40] [$x2+0]
	lw	t3, 20(sp)                      # 4-byte Folded Reload
.Ltmp22:
	#DEBUG_VALUE: fullAdder1:pi1 <- $x28
	lw	t2, 16(sp)                      # 4-byte Folded Reload
.Ltmp23:
	#DEBUG_VALUE: fullAdder1:pi3 <- $x7
	.loc	0 28 2 is_stmt 1                # fulladder1.c:28:2
	#APP
	xor	t1, t2, t3
	not	t1, t1
	#NO_APP
.Ltmp24:
	#DEBUG_VALUE: fullAdder1:new_n18 <- $x6
	.loc	0 0 2 is_stmt 0                 # fulladder1.c:0:2
	lw	t0, 40(sp)                      # 4-byte Folded Reload
.Ltmp25:
	#DEBUG_VALUE: fullAdder1:new_n17 <- $x5
	.loc	0 29 2 is_stmt 1                # fulladder1.c:29:2
	#APP
	xor	t0, t1, t0
	not	t0, t0
	#NO_APP
.Ltmp26:
	#DEBUG_VALUE: fullAdder1:po1 <- $x5
	#DEBUG_VALUE: fullAdder1:new_n17 <- [DW_OP_plus_uconst 40] [$x2+0]
	.loc	0 0 2 is_stmt 0                 # fulladder1.c:0:2
	sw	t0, 12(sp)                      # 4-byte Folded Spill
.Ltmp27:
	#DEBUG_VALUE: fullAdder1:po1 <- [DW_OP_plus_uconst 12] [$x2+0]
	#DEBUG_VALUE: fullAdder1:po1 <- [DW_OP_plus_uconst 12] [$x2+0]
	.loc	0 30 2 is_stmt 1                # fulladder1.c:30:2
	#APP
	and	t3, t2, t3
	#NO_APP
.Ltmp28:
	#DEBUG_VALUE: fullAdder1:new_n20 <- $x28
	.loc	0 31 2                          # fulladder1.c:31:2
	#APP
	not	t3, t3
	#NO_APP
.Ltmp29:
	#DEBUG_VALUE: fullAdder1:new_n21 <- $x28
	.loc	0 32 2                          # fulladder1.c:32:2
	#APP
	not	t1, t1
	#NO_APP
.Ltmp30:
	#DEBUG_VALUE: fullAdder1:new_n22 <- $x6
	.loc	0 0 2 is_stmt 0                 # fulladder1.c:0:2
	lw	t0, 40(sp)                      # 4-byte Folded Reload
.Ltmp31:
	#DEBUG_VALUE: fullAdder1:new_n17 <- $x5
	.loc	0 33 2 is_stmt 1                # fulladder1.c:33:2
	#APP
	and	t0, t1, t0
	#NO_APP
.Ltmp32:
	#DEBUG_VALUE: fullAdder1:new_n23 <- $x5
	.loc	0 34 2                          # fulladder1.c:34:2
	#APP
	not	t0, t0
	#NO_APP
.Ltmp33:
	#DEBUG_VALUE: fullAdder1:new_n24 <- $x5
	.loc	0 35 2                          # fulladder1.c:35:2
	#APP
	and	t0, t0, t3
	#NO_APP
.Ltmp34:
	#DEBUG_VALUE: fullAdder1:new_n25 <- $x5
	.loc	0 37 2                          # fulladder1.c:37:2
	#APP
	########## END ##########
	#NO_APP
	lw	a0, 28(sp)                      # 4-byte Folded Reload
.Ltmp35:
	#DEBUG_VALUE: fullAdder1:po0_p <- $x10
	.loc	0 0 2 is_stmt 0                 # fulladder1.c:0:2
	lw	a1, 24(sp)                      # 4-byte Folded Reload
.Ltmp36:
	#DEBUG_VALUE: fullAdder1:po0 <- $x11
	.loc	0 39 9 is_stmt 1                # fulladder1.c:39:9
	sw	a1, 0(a0)
	lw	a0, 32(sp)                      # 4-byte Folded Reload
.Ltmp37:
	#DEBUG_VALUE: fullAdder1:po1_p <- $x10
	.loc	0 0 9 is_stmt 0                 # fulladder1.c:0:9
	lw	a1, 12(sp)                      # 4-byte Folded Reload
.Ltmp38:
	#DEBUG_VALUE: fullAdder1:po1 <- $x11
	.loc	0 40 9 is_stmt 1                # fulladder1.c:40:9
	sw	a1, 0(a0)
	.loc	0 36 2                          # fulladder1.c:36:2
	#APP
	not	t0, t0
	#NO_APP
.Ltmp39:
	#DEBUG_VALUE: fullAdder1:po2 <- $x5
	.loc	0 0 2 is_stmt 0                 # fulladder1.c:0:2
	lw	a0, 36(sp)                      # 4-byte Folded Reload
.Ltmp40:
	#DEBUG_VALUE: fullAdder1:po2_p <- $x10
	.loc	0 41 9 is_stmt 1                # fulladder1.c:41:9
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
	.loc	0 42 1 epilogue_begin           # fulladder1.c:42:1
	addi	sp, sp, 96
	ret
.Ltmp41:
.Lfunc_end0:
	.size	fullAdder1, .Lfunc_end0-fullAdder1
	.cfi_endproc
                                        # -- End function
	.section	.debug_loclists,"",@progbits
	.word	.Ldebug_list_header_end0-.Ldebug_list_header_start0 # Length
.Ldebug_list_header_start0:
	.half	5                               # Version
	.byte	4                               # Address size
	.byte	0                               # Segment selector size
	.word	31                              # Offset entry count
.Lloclists_table_base0:
	.word	.Ldebug_loc0-.Lloclists_table_base0
	.word	.Ldebug_loc1-.Lloclists_table_base0
	.word	.Ldebug_loc2-.Lloclists_table_base0
	.word	.Ldebug_loc3-.Lloclists_table_base0
	.word	.Ldebug_loc4-.Lloclists_table_base0
	.word	.Ldebug_loc5-.Lloclists_table_base0
	.word	.Ldebug_loc6-.Lloclists_table_base0
	.word	.Ldebug_loc7-.Lloclists_table_base0
	.word	.Ldebug_loc8-.Lloclists_table_base0
	.word	.Ldebug_loc9-.Lloclists_table_base0
	.word	.Ldebug_loc10-.Lloclists_table_base0
	.word	.Ldebug_loc11-.Lloclists_table_base0
	.word	.Ldebug_loc12-.Lloclists_table_base0
	.word	.Ldebug_loc13-.Lloclists_table_base0
	.word	.Ldebug_loc14-.Lloclists_table_base0
	.word	.Ldebug_loc15-.Lloclists_table_base0
	.word	.Ldebug_loc16-.Lloclists_table_base0
	.word	.Ldebug_loc17-.Lloclists_table_base0
	.word	.Ldebug_loc18-.Lloclists_table_base0
	.word	.Ldebug_loc19-.Lloclists_table_base0
	.word	.Ldebug_loc20-.Lloclists_table_base0
	.word	.Ldebug_loc21-.Lloclists_table_base0
	.word	.Ldebug_loc22-.Lloclists_table_base0
	.word	.Ldebug_loc23-.Lloclists_table_base0
	.word	.Ldebug_loc24-.Lloclists_table_base0
	.word	.Ldebug_loc25-.Lloclists_table_base0
	.word	.Ldebug_loc26-.Lloclists_table_base0
	.word	.Ldebug_loc27-.Lloclists_table_base0
	.word	.Ldebug_loc28-.Lloclists_table_base0
	.word	.Ldebug_loc29-.Lloclists_table_base0
	.word	.Ldebug_loc30-.Lloclists_table_base0
.Ldebug_loc0:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Lfunc_begin0-.Lfunc_begin0    #   starting offset
	.uleb128 .Ltmp4-.Lfunc_begin0           #   ending offset
	.byte	1                               # Loc expr size
	.byte	90                              # DW_OP_reg10
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc1:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Lfunc_begin0-.Lfunc_begin0    #   starting offset
	.uleb128 .Ltmp10-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	91                              # DW_OP_reg11
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc2:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Lfunc_begin0-.Lfunc_begin0    #   starting offset
	.uleb128 .Ltmp10-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	92                              # DW_OP_reg12
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc3:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Lfunc_begin0-.Lfunc_begin0    #   starting offset
	.uleb128 .Ltmp10-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	93                              # DW_OP_reg13
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc4:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Lfunc_begin0-.Lfunc_begin0    #   starting offset
	.uleb128 .Ltmp10-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	94                              # DW_OP_reg14
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc5:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Lfunc_begin0-.Lfunc_begin0    #   starting offset
	.uleb128 .Ltmp2-.Lfunc_begin0           #   ending offset
	.byte	1                               # Loc expr size
	.byte	95                              # DW_OP_reg15
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp2-.Lfunc_begin0           #   starting offset
	.uleb128 .Ltmp35-.Lfunc_begin0          #   ending offset
	.byte	2                               # Loc expr size
	.byte	114                             # DW_OP_breg2
	.byte	28                              # 28
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp35-.Lfunc_begin0          #   starting offset
	.uleb128 .Ltmp37-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	90                              # DW_OP_reg10
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc6:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Lfunc_begin0-.Lfunc_begin0    #   starting offset
	.uleb128 .Ltmp1-.Lfunc_begin0           #   ending offset
	.byte	1                               # Loc expr size
	.byte	96                              # DW_OP_reg16
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp1-.Lfunc_begin0           #   starting offset
	.uleb128 .Ltmp37-.Lfunc_begin0          #   ending offset
	.byte	2                               # Loc expr size
	.byte	114                             # DW_OP_breg2
	.byte	32                              # 32
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp37-.Lfunc_begin0          #   starting offset
	.uleb128 .Ltmp39-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	90                              # DW_OP_reg10
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc7:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Lfunc_begin0-.Lfunc_begin0    #   starting offset
	.uleb128 .Ltmp0-.Lfunc_begin0           #   ending offset
	.byte	1                               # Loc expr size
	.byte	97                              # DW_OP_reg17
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp0-.Lfunc_begin0           #   starting offset
	.uleb128 .Ltmp40-.Lfunc_begin0          #   ending offset
	.byte	2                               # Loc expr size
	.byte	114                             # DW_OP_breg2
	.byte	36                              # 36
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp40-.Lfunc_begin0          #   starting offset
	.uleb128 .Lfunc_end0-.Lfunc_begin0      #   ending offset
	.byte	1                               # Loc expr size
	.byte	90                              # DW_OP_reg10
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc8:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp3-.Lfunc_begin0           #   starting offset
	.uleb128 .Ltmp13-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	85                              # DW_OP_reg5
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp13-.Lfunc_begin0          #   starting offset
	.uleb128 .Ltmp23-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	87                              # DW_OP_reg7
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc9:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp4-.Lfunc_begin0           #   starting offset
	.uleb128 .Ltmp5-.Lfunc_begin0           #   ending offset
	.byte	1                               # Loc expr size
	.byte	90                              # DW_OP_reg10
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp5-.Lfunc_begin0           #   starting offset
	.uleb128 .Ltmp22-.Lfunc_begin0          #   ending offset
	.byte	2                               # Loc expr size
	.byte	114                             # DW_OP_breg2
	.byte	20                              # 20
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp22-.Lfunc_begin0          #   starting offset
	.uleb128 .Ltmp28-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	108                             # DW_OP_reg28
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc10:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp6-.Lfunc_begin0           #   starting offset
	.uleb128 .Ltmp14-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	86                              # DW_OP_reg6
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc11:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp7-.Lfunc_begin0           #   starting offset
	.uleb128 .Ltmp22-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	108                             # DW_OP_reg28
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc12:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp8-.Lfunc_begin0           #   starting offset
	.uleb128 .Ltmp9-.Lfunc_begin0           #   ending offset
	.byte	1                               # Loc expr size
	.byte	90                              # DW_OP_reg10
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp9-.Lfunc_begin0           #   starting offset
	.uleb128 .Ltmp23-.Lfunc_begin0          #   ending offset
	.byte	2                               # Loc expr size
	.byte	114                             # DW_OP_breg2
	.byte	16                              # 16
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp23-.Lfunc_begin0          #   starting offset
	.uleb128 .Lfunc_end0-.Lfunc_begin0      #   ending offset
	.byte	1                               # Loc expr size
	.byte	87                              # DW_OP_reg7
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc13:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp10-.Lfunc_begin0          #   starting offset
	.uleb128 .Ltmp16-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	85                              # DW_OP_reg5
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc14:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp11-.Lfunc_begin0          #   starting offset
	.uleb128 .Ltmp12-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	87                              # DW_OP_reg7
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp12-.Lfunc_begin0          #   starting offset
	.uleb128 .Ltmp36-.Lfunc_begin0          #   ending offset
	.byte	2                               # Loc expr size
	.byte	114                             # DW_OP_breg2
	.byte	24                              # 24
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp36-.Lfunc_begin0          #   starting offset
	.uleb128 .Ltmp38-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	91                              # DW_OP_reg11
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc15:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp14-.Lfunc_begin0          #   starting offset
	.uleb128 .Ltmp15-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	86                              # DW_OP_reg6
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc16:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp15-.Lfunc_begin0          #   starting offset
	.uleb128 .Ltmp24-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	86                              # DW_OP_reg6
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc17:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp16-.Lfunc_begin0          #   starting offset
	.uleb128 .Ltmp17-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	85                              # DW_OP_reg5
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc18:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp17-.Lfunc_begin0          #   starting offset
	.uleb128 .Ltmp18-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	85                              # DW_OP_reg5
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc19:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp18-.Lfunc_begin0          #   starting offset
	.uleb128 .Ltmp19-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	85                              # DW_OP_reg5
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc20:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp19-.Lfunc_begin0          #   starting offset
	.uleb128 .Ltmp20-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	85                              # DW_OP_reg5
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc21:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp20-.Lfunc_begin0          #   starting offset
	.uleb128 .Ltmp21-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	85                              # DW_OP_reg5
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp21-.Lfunc_begin0          #   starting offset
	.uleb128 .Ltmp25-.Lfunc_begin0          #   ending offset
	.byte	2                               # Loc expr size
	.byte	114                             # DW_OP_breg2
	.byte	40                              # 40
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp25-.Lfunc_begin0          #   starting offset
	.uleb128 .Ltmp26-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	85                              # DW_OP_reg5
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp26-.Lfunc_begin0          #   starting offset
	.uleb128 .Ltmp31-.Lfunc_begin0          #   ending offset
	.byte	2                               # Loc expr size
	.byte	114                             # DW_OP_breg2
	.byte	40                              # 40
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp31-.Lfunc_begin0          #   starting offset
	.uleb128 .Ltmp32-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	85                              # DW_OP_reg5
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc22:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp24-.Lfunc_begin0          #   starting offset
	.uleb128 .Ltmp30-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	86                              # DW_OP_reg6
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc23:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp26-.Lfunc_begin0          #   starting offset
	.uleb128 .Ltmp27-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	85                              # DW_OP_reg5
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp27-.Lfunc_begin0          #   starting offset
	.uleb128 .Ltmp38-.Lfunc_begin0          #   ending offset
	.byte	2                               # Loc expr size
	.byte	114                             # DW_OP_breg2
	.byte	12                              # 12
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp38-.Lfunc_begin0          #   starting offset
	.uleb128 .Ltmp39-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	91                              # DW_OP_reg11
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc24:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp28-.Lfunc_begin0          #   starting offset
	.uleb128 .Ltmp29-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	108                             # DW_OP_reg28
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc25:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp29-.Lfunc_begin0          #   starting offset
	.uleb128 .Lfunc_end0-.Lfunc_begin0      #   ending offset
	.byte	1                               # Loc expr size
	.byte	108                             # DW_OP_reg28
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc26:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp30-.Lfunc_begin0          #   starting offset
	.uleb128 .Lfunc_end0-.Lfunc_begin0      #   ending offset
	.byte	1                               # Loc expr size
	.byte	86                              # DW_OP_reg6
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc27:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp32-.Lfunc_begin0          #   starting offset
	.uleb128 .Ltmp33-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	85                              # DW_OP_reg5
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc28:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp33-.Lfunc_begin0          #   starting offset
	.uleb128 .Ltmp34-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	85                              # DW_OP_reg5
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc29:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp34-.Lfunc_begin0          #   starting offset
	.uleb128 .Ltmp39-.Lfunc_begin0          #   ending offset
	.byte	1                               # Loc expr size
	.byte	85                              # DW_OP_reg5
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_loc30:
	.byte	4                               # DW_LLE_offset_pair
	.uleb128 .Ltmp39-.Lfunc_begin0          #   starting offset
	.uleb128 .Lfunc_end0-.Lfunc_begin0      #   ending offset
	.byte	1                               # Loc expr size
	.byte	85                              # DW_OP_reg5
	.byte	0                               # DW_LLE_end_of_list
.Ldebug_list_header_end0:
	.section	.debug_abbrev,"",@progbits
	.byte	1                               # Abbreviation Code
	.byte	17                              # DW_TAG_compile_unit
	.byte	1                               # DW_CHILDREN_yes
	.byte	37                              # DW_AT_producer
	.byte	37                              # DW_FORM_strx1
	.byte	19                              # DW_AT_language
	.byte	5                               # DW_FORM_data2
	.byte	3                               # DW_AT_name
	.byte	37                              # DW_FORM_strx1
	.byte	114                             # DW_AT_str_offsets_base
	.byte	23                              # DW_FORM_sec_offset
	.byte	16                              # DW_AT_stmt_list
	.byte	23                              # DW_FORM_sec_offset
	.byte	27                              # DW_AT_comp_dir
	.byte	37                              # DW_FORM_strx1
	.byte	17                              # DW_AT_low_pc
	.byte	27                              # DW_FORM_addrx
	.byte	18                              # DW_AT_high_pc
	.byte	6                               # DW_FORM_data4
	.byte	115                             # DW_AT_addr_base
	.byte	23                              # DW_FORM_sec_offset
	.ascii	"\214\001"                      # DW_AT_loclists_base
	.byte	23                              # DW_FORM_sec_offset
	.byte	0                               # EOM(1)
	.byte	0                               # EOM(2)
	.byte	2                               # Abbreviation Code
	.byte	46                              # DW_TAG_subprogram
	.byte	1                               # DW_CHILDREN_yes
	.byte	17                              # DW_AT_low_pc
	.byte	27                              # DW_FORM_addrx
	.byte	18                              # DW_AT_high_pc
	.byte	6                               # DW_FORM_data4
	.byte	64                              # DW_AT_frame_base
	.byte	24                              # DW_FORM_exprloc
	.byte	122                             # DW_AT_call_all_calls
	.byte	25                              # DW_FORM_flag_present
	.byte	3                               # DW_AT_name
	.byte	37                              # DW_FORM_strx1
	.byte	58                              # DW_AT_decl_file
	.byte	11                              # DW_FORM_data1
	.byte	59                              # DW_AT_decl_line
	.byte	11                              # DW_FORM_data1
	.byte	39                              # DW_AT_prototyped
	.byte	25                              # DW_FORM_flag_present
	.byte	63                              # DW_AT_external
	.byte	25                              # DW_FORM_flag_present
	.byte	0                               # EOM(1)
	.byte	0                               # EOM(2)
	.byte	3                               # Abbreviation Code
	.byte	5                               # DW_TAG_formal_parameter
	.byte	0                               # DW_CHILDREN_no
	.byte	2                               # DW_AT_location
	.byte	34                              # DW_FORM_loclistx
	.byte	3                               # DW_AT_name
	.byte	37                              # DW_FORM_strx1
	.byte	58                              # DW_AT_decl_file
	.byte	11                              # DW_FORM_data1
	.byte	59                              # DW_AT_decl_line
	.byte	11                              # DW_FORM_data1
	.byte	73                              # DW_AT_type
	.byte	19                              # DW_FORM_ref4
	.byte	0                               # EOM(1)
	.byte	0                               # EOM(2)
	.byte	4                               # Abbreviation Code
	.byte	52                              # DW_TAG_variable
	.byte	0                               # DW_CHILDREN_no
	.byte	2                               # DW_AT_location
	.byte	34                              # DW_FORM_loclistx
	.byte	3                               # DW_AT_name
	.byte	37                              # DW_FORM_strx1
	.byte	58                              # DW_AT_decl_file
	.byte	11                              # DW_FORM_data1
	.byte	59                              # DW_AT_decl_line
	.byte	11                              # DW_FORM_data1
	.byte	73                              # DW_AT_type
	.byte	19                              # DW_FORM_ref4
	.byte	0                               # EOM(1)
	.byte	0                               # EOM(2)
	.byte	5                               # Abbreviation Code
	.byte	15                              # DW_TAG_pointer_type
	.byte	0                               # DW_CHILDREN_no
	.byte	73                              # DW_AT_type
	.byte	19                              # DW_FORM_ref4
	.byte	0                               # EOM(1)
	.byte	0                               # EOM(2)
	.byte	6                               # Abbreviation Code
	.byte	36                              # DW_TAG_base_type
	.byte	0                               # DW_CHILDREN_no
	.byte	3                               # DW_AT_name
	.byte	37                              # DW_FORM_strx1
	.byte	62                              # DW_AT_encoding
	.byte	11                              # DW_FORM_data1
	.byte	11                              # DW_AT_byte_size
	.byte	11                              # DW_FORM_data1
	.byte	0                               # EOM(1)
	.byte	0                               # EOM(2)
	.byte	0                               # EOM(3)
	.section	.debug_info,"",@progbits
.Lcu_begin0:
	.word	.Ldebug_info_end0-.Ldebug_info_start0 # Length of Unit
.Ldebug_info_start0:
	.half	5                               # DWARF version number
	.byte	1                               # DWARF Unit Type
	.byte	4                               # Address Size (in bytes)
	.word	.debug_abbrev                   # Offset Into Abbrev. Section
	.byte	1                               # Abbrev [1] 0xc:0x148 DW_TAG_compile_unit
	.byte	0                               # DW_AT_producer
	.half	29                              # DW_AT_language
	.byte	1                               # DW_AT_name
	.word	.Lstr_offsets_base0             # DW_AT_str_offsets_base
	.word	.Lline_table_start0             # DW_AT_stmt_list
	.byte	2                               # DW_AT_comp_dir
	.byte	0                               # DW_AT_low_pc
	.word	.Lfunc_end0-.Lfunc_begin0       # DW_AT_high_pc
	.word	.Laddr_table_base0              # DW_AT_addr_base
	.word	.Lloclists_table_base0          # DW_AT_loclists_base
	.byte	2                               # Abbrev [2] 0x27:0x123 DW_TAG_subprogram
	.byte	0                               # DW_AT_low_pc
	.word	.Lfunc_end0-.Lfunc_begin0       # DW_AT_high_pc
	.byte	1                               # DW_AT_frame_base
	.byte	82
                                        # DW_AT_call_all_calls
	.byte	3                               # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	3                               # DW_AT_decl_line
                                        # DW_AT_prototyped
                                        # DW_AT_external
	.byte	3                               # Abbrev [3] 0x32:0x9 DW_TAG_formal_parameter
	.byte	0                               # DW_AT_location
	.byte	4                               # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	4                               # DW_AT_decl_line
	.word	330                             # DW_AT_type
	.byte	3                               # Abbrev [3] 0x3b:0x9 DW_TAG_formal_parameter
	.byte	1                               # DW_AT_location
	.byte	6                               # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	5                               # DW_AT_decl_line
	.word	330                             # DW_AT_type
	.byte	3                               # Abbrev [3] 0x44:0x9 DW_TAG_formal_parameter
	.byte	2                               # DW_AT_location
	.byte	7                               # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	6                               # DW_AT_decl_line
	.word	330                             # DW_AT_type
	.byte	3                               # Abbrev [3] 0x4d:0x9 DW_TAG_formal_parameter
	.byte	3                               # DW_AT_location
	.byte	8                               # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	7                               # DW_AT_decl_line
	.word	330                             # DW_AT_type
	.byte	3                               # Abbrev [3] 0x56:0x9 DW_TAG_formal_parameter
	.byte	4                               # DW_AT_location
	.byte	9                               # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	8                               # DW_AT_decl_line
	.word	330                             # DW_AT_type
	.byte	3                               # Abbrev [3] 0x5f:0x9 DW_TAG_formal_parameter
	.byte	5                               # DW_AT_location
	.byte	10                              # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	9                               # DW_AT_decl_line
	.word	330                             # DW_AT_type
	.byte	3                               # Abbrev [3] 0x68:0x9 DW_TAG_formal_parameter
	.byte	6                               # DW_AT_location
	.byte	11                              # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	10                              # DW_AT_decl_line
	.word	330                             # DW_AT_type
	.byte	3                               # Abbrev [3] 0x71:0x9 DW_TAG_formal_parameter
	.byte	7                               # DW_AT_location
	.byte	12                              # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	11                              # DW_AT_decl_line
	.word	330                             # DW_AT_type
	.byte	4                               # Abbrev [4] 0x7a:0x9 DW_TAG_variable
	.byte	8                               # DW_AT_location
	.byte	13                              # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	15                              # DW_AT_decl_line
	.word	335                             # DW_AT_type
	.byte	4                               # Abbrev [4] 0x83:0x9 DW_TAG_variable
	.byte	9                               # DW_AT_location
	.byte	14                              # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	15                              # DW_AT_decl_line
	.word	335                             # DW_AT_type
	.byte	4                               # Abbrev [4] 0x8c:0x9 DW_TAG_variable
	.byte	10                              # DW_AT_location
	.byte	15                              # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	15                              # DW_AT_decl_line
	.word	335                             # DW_AT_type
	.byte	4                               # Abbrev [4] 0x95:0x9 DW_TAG_variable
	.byte	11                              # DW_AT_location
	.byte	16                              # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	15                              # DW_AT_decl_line
	.word	335                             # DW_AT_type
	.byte	4                               # Abbrev [4] 0x9e:0x9 DW_TAG_variable
	.byte	12                              # DW_AT_location
	.byte	17                              # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	15                              # DW_AT_decl_line
	.word	335                             # DW_AT_type
	.byte	4                               # Abbrev [4] 0xa7:0x9 DW_TAG_variable
	.byte	13                              # DW_AT_location
	.byte	18                              # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	14                              # DW_AT_decl_line
	.word	335                             # DW_AT_type
	.byte	4                               # Abbrev [4] 0xb0:0x9 DW_TAG_variable
	.byte	14                              # DW_AT_location
	.byte	19                              # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	16                              # DW_AT_decl_line
	.word	335                             # DW_AT_type
	.byte	4                               # Abbrev [4] 0xb9:0x9 DW_TAG_variable
	.byte	15                              # DW_AT_location
	.byte	20                              # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	14                              # DW_AT_decl_line
	.word	335                             # DW_AT_type
	.byte	4                               # Abbrev [4] 0xc2:0x9 DW_TAG_variable
	.byte	16                              # DW_AT_location
	.byte	21                              # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	14                              # DW_AT_decl_line
	.word	335                             # DW_AT_type
	.byte	4                               # Abbrev [4] 0xcb:0x9 DW_TAG_variable
	.byte	17                              # DW_AT_location
	.byte	22                              # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	14                              # DW_AT_decl_line
	.word	335                             # DW_AT_type
	.byte	4                               # Abbrev [4] 0xd4:0x9 DW_TAG_variable
	.byte	18                              # DW_AT_location
	.byte	23                              # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	14                              # DW_AT_decl_line
	.word	335                             # DW_AT_type
	.byte	4                               # Abbrev [4] 0xdd:0x9 DW_TAG_variable
	.byte	19                              # DW_AT_location
	.byte	24                              # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	14                              # DW_AT_decl_line
	.word	335                             # DW_AT_type
	.byte	4                               # Abbrev [4] 0xe6:0x9 DW_TAG_variable
	.byte	20                              # DW_AT_location
	.byte	25                              # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	14                              # DW_AT_decl_line
	.word	335                             # DW_AT_type
	.byte	4                               # Abbrev [4] 0xef:0x9 DW_TAG_variable
	.byte	21                              # DW_AT_location
	.byte	26                              # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	14                              # DW_AT_decl_line
	.word	335                             # DW_AT_type
	.byte	4                               # Abbrev [4] 0xf8:0x9 DW_TAG_variable
	.byte	22                              # DW_AT_location
	.byte	27                              # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	14                              # DW_AT_decl_line
	.word	335                             # DW_AT_type
	.byte	4                               # Abbrev [4] 0x101:0x9 DW_TAG_variable
	.byte	23                              # DW_AT_location
	.byte	28                              # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	16                              # DW_AT_decl_line
	.word	335                             # DW_AT_type
	.byte	4                               # Abbrev [4] 0x10a:0x9 DW_TAG_variable
	.byte	24                              # DW_AT_location
	.byte	29                              # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	14                              # DW_AT_decl_line
	.word	335                             # DW_AT_type
	.byte	4                               # Abbrev [4] 0x113:0x9 DW_TAG_variable
	.byte	25                              # DW_AT_location
	.byte	30                              # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	14                              # DW_AT_decl_line
	.word	335                             # DW_AT_type
	.byte	4                               # Abbrev [4] 0x11c:0x9 DW_TAG_variable
	.byte	26                              # DW_AT_location
	.byte	31                              # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	14                              # DW_AT_decl_line
	.word	335                             # DW_AT_type
	.byte	4                               # Abbrev [4] 0x125:0x9 DW_TAG_variable
	.byte	27                              # DW_AT_location
	.byte	32                              # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	14                              # DW_AT_decl_line
	.word	335                             # DW_AT_type
	.byte	4                               # Abbrev [4] 0x12e:0x9 DW_TAG_variable
	.byte	28                              # DW_AT_location
	.byte	33                              # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	14                              # DW_AT_decl_line
	.word	335                             # DW_AT_type
	.byte	4                               # Abbrev [4] 0x137:0x9 DW_TAG_variable
	.byte	29                              # DW_AT_location
	.byte	34                              # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	14                              # DW_AT_decl_line
	.word	335                             # DW_AT_type
	.byte	4                               # Abbrev [4] 0x140:0x9 DW_TAG_variable
	.byte	30                              # DW_AT_location
	.byte	35                              # DW_AT_name
	.byte	0                               # DW_AT_decl_file
	.byte	16                              # DW_AT_decl_line
	.word	335                             # DW_AT_type
	.byte	0                               # End Of Children Mark
	.byte	5                               # Abbrev [5] 0x14a:0x5 DW_TAG_pointer_type
	.word	335                             # DW_AT_type
	.byte	6                               # Abbrev [6] 0x14f:0x4 DW_TAG_base_type
	.byte	5                               # DW_AT_name
	.byte	5                               # DW_AT_encoding
	.byte	4                               # DW_AT_byte_size
	.byte	0                               # End Of Children Mark
.Ldebug_info_end0:
	.section	.debug_str_offsets,"",@progbits
	.word	148                             # Length of String Offsets Set
	.half	5
	.half	0
.Lstr_offsets_base0:
	.section	.debug_str,"MS",@progbits,1
.Linfo_string0:
	.asciz	"clang version 20.0.0git (https://github.com/llvm/llvm-project.git d550ada5ab6cd6e49de71ac4c9aa27ced4c11de0)" # string offset=0
.Linfo_string1:
	.asciz	"fulladder1.c"                  # string offset=108
.Linfo_string2:
	.asciz	"/u/uab9qt/worktable/llvm_repos/bit-serial-compiler/step3-circuit-to-asm/1bit_full_adder" # string offset=121
.Linfo_string3:
	.asciz	"fullAdder1"                    # string offset=209
.Linfo_string4:
	.asciz	"pi0_p"                         # string offset=220
.Linfo_string5:
	.asciz	"int"                           # string offset=226
.Linfo_string6:
	.asciz	"pi1_p"                         # string offset=230
.Linfo_string7:
	.asciz	"pi2_p"                         # string offset=236
.Linfo_string8:
	.asciz	"pi3_p"                         # string offset=242
.Linfo_string9:
	.asciz	"pi4_p"                         # string offset=248
.Linfo_string10:
	.asciz	"po0_p"                         # string offset=254
.Linfo_string11:
	.asciz	"po1_p"                         # string offset=260
.Linfo_string12:
	.asciz	"po2_p"                         # string offset=266
.Linfo_string13:
	.asciz	"pi0"                           # string offset=272
.Linfo_string14:
	.asciz	"pi1"                           # string offset=276
.Linfo_string15:
	.asciz	"pi2"                           # string offset=280
.Linfo_string16:
	.asciz	"pi4"                           # string offset=284
.Linfo_string17:
	.asciz	"pi3"                           # string offset=288
.Linfo_string18:
	.asciz	"new_n9"                        # string offset=292
.Linfo_string19:
	.asciz	"po0"                           # string offset=299
.Linfo_string20:
	.asciz	"new_n11"                       # string offset=303
.Linfo_string21:
	.asciz	"new_n12"                       # string offset=311
.Linfo_string22:
	.asciz	"new_n13"                       # string offset=319
.Linfo_string23:
	.asciz	"new_n14"                       # string offset=327
.Linfo_string24:
	.asciz	"new_n15"                       # string offset=335
.Linfo_string25:
	.asciz	"new_n16"                       # string offset=343
.Linfo_string26:
	.asciz	"new_n17"                       # string offset=351
.Linfo_string27:
	.asciz	"new_n18"                       # string offset=359
.Linfo_string28:
	.asciz	"po1"                           # string offset=367
.Linfo_string29:
	.asciz	"new_n20"                       # string offset=371
.Linfo_string30:
	.asciz	"new_n21"                       # string offset=379
.Linfo_string31:
	.asciz	"new_n22"                       # string offset=387
.Linfo_string32:
	.asciz	"new_n23"                       # string offset=395
.Linfo_string33:
	.asciz	"new_n24"                       # string offset=403
.Linfo_string34:
	.asciz	"new_n25"                       # string offset=411
.Linfo_string35:
	.asciz	"po2"                           # string offset=419
	.section	.debug_str_offsets,"",@progbits
	.word	.Linfo_string0
	.word	.Linfo_string1
	.word	.Linfo_string2
	.word	.Linfo_string3
	.word	.Linfo_string4
	.word	.Linfo_string5
	.word	.Linfo_string6
	.word	.Linfo_string7
	.word	.Linfo_string8
	.word	.Linfo_string9
	.word	.Linfo_string10
	.word	.Linfo_string11
	.word	.Linfo_string12
	.word	.Linfo_string13
	.word	.Linfo_string14
	.word	.Linfo_string15
	.word	.Linfo_string16
	.word	.Linfo_string17
	.word	.Linfo_string18
	.word	.Linfo_string19
	.word	.Linfo_string20
	.word	.Linfo_string21
	.word	.Linfo_string22
	.word	.Linfo_string23
	.word	.Linfo_string24
	.word	.Linfo_string25
	.word	.Linfo_string26
	.word	.Linfo_string27
	.word	.Linfo_string28
	.word	.Linfo_string29
	.word	.Linfo_string30
	.word	.Linfo_string31
	.word	.Linfo_string32
	.word	.Linfo_string33
	.word	.Linfo_string34
	.word	.Linfo_string35
	.section	.debug_addr,"",@progbits
	.word	.Ldebug_addr_end0-.Ldebug_addr_start0 # Length of contribution
.Ldebug_addr_start0:
	.half	5                               # DWARF version number
	.byte	4                               # Address size
	.byte	0                               # Segment selector size
.Laddr_table_base0:
	.word	.Lfunc_begin0
.Ldebug_addr_end0:
	.ident	"clang version 20.0.0git (https://github.com/llvm/llvm-project.git d550ada5ab6cd6e49de71ac4c9aa27ced4c11de0)"
	.section	".note.GNU-stack","",@progbits
	.addrsig
	.section	.debug_line,"",@progbits
.Lline_table_start0:
