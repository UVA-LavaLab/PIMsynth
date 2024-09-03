; ModuleID = 'fulladder2.cpp'
source_filename = "fulladder2.cpp"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

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
  %32 = alloca i64, align 8
  %33 = alloca i64, align 8
  %34 = alloca i64, align 8
  %35 = alloca i64, align 8
  %36 = alloca i64, align 8
  %37 = alloca i64, align 8
  %38 = alloca i64, align 8
  %39 = alloca i64, align 8
  %40 = alloca i64, align 8
  %41 = alloca i64, align 8
  %42 = alloca i64, align 8
  %43 = alloca i64, align 8
  store i64 %0, ptr %9, align 8
  store i64 %1, ptr %10, align 8
  store i64 %2, ptr %11, align 8
  store i64 %3, ptr %12, align 8
  store i64 %4, ptr %13, align 8
  store ptr %5, ptr %14, align 8
  store ptr %6, ptr %15, align 8
  store ptr %7, ptr %16, align 8
  %44 = load i64, ptr %11, align 8
  %45 = xor i64 %44, -1
  store i64 %45, ptr %17, align 8
  %46 = load i64, ptr %17, align 8
  %47 = load i64, ptr %9, align 8
  %48 = or i64 %46, %47
  %49 = xor i64 %48, -1
  store i64 %49, ptr %18, align 8
  %50 = load i64, ptr %9, align 8
  %51 = xor i64 %50, -1
  store i64 %51, ptr %19, align 8
  %52 = load i64, ptr %11, align 8
  %53 = load i64, ptr %19, align 8
  %54 = or i64 %52, %53
  %55 = xor i64 %54, -1
  store i64 %55, ptr %20, align 8
  %56 = load i64, ptr %20, align 8
  %57 = load i64, ptr %18, align 8
  %58 = or i64 %56, %57
  %59 = xor i64 %58, -1
  store i64 %59, ptr %21, align 8
  %60 = load i64, ptr %21, align 8
  %61 = load i64, ptr %13, align 8
  %62 = and i64 %60, %61
  %63 = xor i64 %62, -1
  store i64 %63, ptr %22, align 8
  %64 = load i64, ptr %13, align 8
  %65 = xor i64 %64, -1
  store i64 %65, ptr %23, align 8
  %66 = load i64, ptr %11, align 8
  %67 = load i64, ptr %19, align 8
  %68 = and i64 %66, %67
  %69 = xor i64 %68, -1
  store i64 %69, ptr %24, align 8
  %70 = load i64, ptr %17, align 8
  %71 = load i64, ptr %9, align 8
  %72 = and i64 %70, %71
  %73 = xor i64 %72, -1
  store i64 %73, ptr %25, align 8
  %74 = load i64, ptr %25, align 8
  %75 = load i64, ptr %24, align 8
  %76 = and i64 %74, %75
  %77 = xor i64 %76, -1
  store i64 %77, ptr %26, align 8
  %78 = load i64, ptr %26, align 8
  %79 = load i64, ptr %23, align 8
  %80 = and i64 %78, %79
  %81 = xor i64 %80, -1
  store i64 %81, ptr %27, align 8
  %82 = load i64, ptr %27, align 8
  %83 = load i64, ptr %22, align 8
  %84 = and i64 %82, %83
  %85 = xor i64 %84, -1
  %86 = load ptr, ptr %14, align 8
  store i64 %85, ptr %86, align 8
  %87 = load i64, ptr %17, align 8
  %88 = load i64, ptr %19, align 8
  %89 = or i64 %87, %88
  %90 = xor i64 %89, -1
  store i64 %90, ptr %28, align 8
  %91 = load i64, ptr %28, align 8
  %92 = xor i64 %91, -1
  store i64 %92, ptr %29, align 8
  %93 = load i64, ptr %26, align 8
  %94 = load i64, ptr %13, align 8
  %95 = and i64 %93, %94
  %96 = xor i64 %95, -1
  store i64 %96, ptr %30, align 8
  %97 = load i64, ptr %30, align 8
  %98 = load i64, ptr %29, align 8
  %99 = and i64 %97, %98
  %100 = xor i64 %99, -1
  store i64 %100, ptr %31, align 8
  %101 = load i64, ptr %12, align 8
  %102 = xor i64 %101, -1
  store i64 %102, ptr %32, align 8
  %103 = load i64, ptr %32, align 8
  %104 = load i64, ptr %10, align 8
  %105 = or i64 %103, %104
  %106 = xor i64 %105, -1
  store i64 %106, ptr %33, align 8
  %107 = load i64, ptr %32, align 8
  %108 = load i64, ptr %10, align 8
  %109 = and i64 %107, %108
  %110 = xor i64 %109, -1
  store i64 %110, ptr %34, align 8
  %111 = load i64, ptr %34, align 8
  %112 = xor i64 %111, -1
  store i64 %112, ptr %35, align 8
  %113 = load i64, ptr %35, align 8
  %114 = load i64, ptr %33, align 8
  %115 = or i64 %113, %114
  %116 = xor i64 %115, -1
  store i64 %116, ptr %36, align 8
  %117 = load i64, ptr %36, align 8
  %118 = load i64, ptr %31, align 8
  %119 = and i64 %117, %118
  %120 = xor i64 %119, -1
  store i64 %120, ptr %37, align 8
  %121 = load i64, ptr %21, align 8
  %122 = load i64, ptr %23, align 8
  %123 = or i64 %121, %122
  %124 = xor i64 %123, -1
  store i64 %124, ptr %38, align 8
  %125 = load i64, ptr %38, align 8
  %126 = load i64, ptr %28, align 8
  %127 = or i64 %125, %126
  %128 = xor i64 %127, -1
  store i64 %128, ptr %39, align 8
  %129 = load i64, ptr %36, align 8
  %130 = xor i64 %129, -1
  store i64 %130, ptr %40, align 8
  %131 = load i64, ptr %40, align 8
  %132 = load i64, ptr %39, align 8
  %133 = and i64 %131, %132
  %134 = xor i64 %133, -1
  store i64 %134, ptr %41, align 8
  %135 = load i64, ptr %41, align 8
  %136 = load i64, ptr %37, align 8
  %137 = and i64 %135, %136
  %138 = xor i64 %137, -1
  %139 = load ptr, ptr %15, align 8
  store i64 %138, ptr %139, align 8
  %140 = load i64, ptr %12, align 8
  %141 = load i64, ptr %10, align 8
  %142 = and i64 %140, %141
  %143 = xor i64 %142, -1
  store i64 %143, ptr %42, align 8
  %144 = load i64, ptr %40, align 8
  %145 = load i64, ptr %31, align 8
  %146 = and i64 %144, %145
  %147 = xor i64 %146, -1
  store i64 %147, ptr %43, align 8
  %148 = load i64, ptr %43, align 8
  %149 = load i64, ptr %42, align 8
  %150 = and i64 %148, %149
  %151 = xor i64 %150, -1
  %152 = load ptr, ptr %16, align 8
  store i64 %151, ptr %152, align 8
  ret void
}

attributes #0 = { mustprogress noinline nounwind optnone uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

!llvm.module.flags = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"PIE Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 2}
!4 = !{i32 7, !"frame-pointer", i32 2}
!5 = !{!"clang version 20.0.0git (https://github.com/llvm/llvm-project.git d550ada5ab6cd6e49de71ac4c9aa27ced4c11de0)"}
