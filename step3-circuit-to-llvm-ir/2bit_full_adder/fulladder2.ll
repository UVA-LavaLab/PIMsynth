; ModuleID = 'fulladder2.cpp'
source_filename = "fulladder2.cpp"
target datalayout = "e-m:e-i8:8:32-i16:16:32-i64:64-i128:128-n32:64-S128-Fn32"
target triple = "aarch64-unknown-linux-gnu"

; Function Attrs: mustprogress noinline nounwind optnone uwtable
define dso_local void @_Z10fullAdder2mmmmmRmS_S_(i64 noundef %0, i64 noundef %1, i64 noundef %2, i64 noundef %3, i64 noundef %4, ptr noundef nonnull align 8 dereferenceable(8) %5, ptr noundef nonnull align 8 dereferenceable(8) %6, ptr noundef nonnull align 8 dereferenceable(8) %7) #0 {
  %9 = alloca i64, align 8
  %10 = alloca i64, align 8
  %11 = alloca i64, align 8
  %12 = alloca i64, align 8
  %13 = alloca i64, align 8
  %14 = alloca ptr, align 8
  %15 = alloca ptr, align 8
  %16 = alloca ptr, align 8
  %17 = alloca i64, align 8
  %18 = alloca i64, align 8
  %19 = alloca i64, align 8
  %20 = alloca i64, align 8
  %21 = alloca i64, align 8
  %22 = alloca i64, align 8
  %23 = alloca i64, align 8
  %24 = alloca i64, align 8
  %25 = alloca i64, align 8
  %26 = alloca i64, align 8
  %27 = alloca i64, align 8
  %28 = alloca i64, align 8
  %29 = alloca i64, align 8
  %30 = alloca i64, align 8
  %31 = alloca i64, align 8
  store i64 %0, ptr %9, align 8
  store i64 %1, ptr %10, align 8
  store i64 %2, ptr %11, align 8
  store i64 %3, ptr %12, align 8
  store i64 %4, ptr %13, align 8
  store ptr %5, ptr %14, align 8
  store ptr %6, ptr %15, align 8
  store ptr %7, ptr %16, align 8
  %32 = load i64, ptr %11, align 8
  %33 = load i64, ptr %9, align 8
  %34 = xor i64 %32, %33
  %35 = xor i64 %34, -1
  store i64 %35, ptr %17, align 8
  %36 = load i64, ptr %17, align 8
  %37 = load i64, ptr %13, align 8
  %38 = xor i64 %36, %37
  %39 = xor i64 %38, -1
  %40 = load ptr, ptr %14, align 8
  store i64 %39, ptr %40, align 8
  %41 = load i64, ptr %11, align 8
  %42 = load i64, ptr %9, align 8
  %43 = and i64 %41, %42
  store i64 %43, ptr %18, align 8
  %44 = load i64, ptr %18, align 8
  %45 = xor i64 %44, -1
  store i64 %45, ptr %19, align 8
  %46 = load i64, ptr %17, align 8
  %47 = xor i64 %46, -1
  store i64 %47, ptr %20, align 8
  %48 = load i64, ptr %20, align 8
  %49 = load i64, ptr %13, align 8
  %50 = and i64 %48, %49
  store i64 %50, ptr %21, align 8
  %51 = load i64, ptr %21, align 8
  %52 = xor i64 %51, -1
  store i64 %52, ptr %22, align 8
  %53 = load i64, ptr %22, align 8
  %54 = load i64, ptr %19, align 8
  %55 = and i64 %53, %54
  store i64 %55, ptr %23, align 8
  %56 = load i64, ptr %23, align 8
  %57 = xor i64 %56, -1
  store i64 %57, ptr %24, align 8
  %58 = load i64, ptr %12, align 8
  %59 = load i64, ptr %10, align 8
  %60 = xor i64 %58, %59
  %61 = xor i64 %60, -1
  store i64 %61, ptr %25, align 8
  %62 = load i64, ptr %25, align 8
  %63 = load i64, ptr %24, align 8
  %64 = xor i64 %62, %63
  %65 = xor i64 %64, -1
  %66 = load ptr, ptr %15, align 8
  store i64 %65, ptr %66, align 8
  %67 = load i64, ptr %12, align 8
  %68 = load i64, ptr %10, align 8
  %69 = and i64 %67, %68
  store i64 %69, ptr %26, align 8
  %70 = load i64, ptr %26, align 8
  %71 = xor i64 %70, -1
  store i64 %71, ptr %27, align 8
  %72 = load i64, ptr %25, align 8
  %73 = xor i64 %72, -1
  store i64 %73, ptr %28, align 8
  %74 = load i64, ptr %28, align 8
  %75 = load i64, ptr %24, align 8
  %76 = and i64 %74, %75
  store i64 %76, ptr %29, align 8
  %77 = load i64, ptr %29, align 8
  %78 = xor i64 %77, -1
  store i64 %78, ptr %30, align 8
  %79 = load i64, ptr %30, align 8
  %80 = load i64, ptr %27, align 8
  %81 = and i64 %79, %80
  store i64 %81, ptr %31, align 8
  %82 = load i64, ptr %31, align 8
  %83 = xor i64 %82, -1
  %84 = load ptr, ptr %16, align 8
  store i64 %83, ptr %84, align 8
  ret void
}

attributes #0 = { mustprogress noinline nounwind optnone uwtable "frame-pointer"="non-leaf" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+fp-armv8,+neon,+outline-atomics,+v8a,-fmv" }

!llvm.module.flags = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"PIE Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 2}
!4 = !{i32 7, !"frame-pointer", i32 1}
!5 = !{!"clang version 20.0.0git (https://github.com/llvm/llvm-project.git d550ada5ab6cd6e49de71ac4c9aa27ced4c11de0)"}
