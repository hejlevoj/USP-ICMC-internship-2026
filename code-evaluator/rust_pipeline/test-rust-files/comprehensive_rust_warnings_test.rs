// Comprehensive Rust test file to trigger ALL compiler warnings from rust-config.json
// DO NOT suppress warnings - we want them all to trigger!

use std::mem;

fn main() {
    test_memory_safety();
    test_undefined_behavior();
    test_type_safety();
    test_control_flow();
    test_logic_errors();
    test_style_idiom();
}

// === MEMORY SAFETY ===

// invalid_reference_casting
fn test_invalid_reference_casting() {
    let x = 5;
    let x_ref = &x;
    let x_mut = unsafe { &mut *(x_ref as *const i32 as *mut i32) };
    *x_mut = 10;
}

// static_mut_refs
static mut STATIC_VAR: i32 = 0;
fn test_static_mut_refs() {
    unsafe {
        let r = &STATIC_VAR;
    }
}

// invalid_value
fn test_invalid_value() {
    unsafe {
        let _x: bool = mem::uninitialized();
    }
}

// fuzzy_provenance_casts
fn test_fuzzy_provenance_casts() {
    let ptr = 0x1234 as *const i32;
}

// lossy_provenance_casts
fn test_lossy_provenance_casts() {
    let ptr: *const i32 = std::ptr::null();
    let addr = ptr as usize;
}

// ambiguous_wide_pointer_comparisons
fn test_ambiguous_wide_pointer() {
    let a: &[i32] = &[1, 2, 3];
    let b: &[i32] = &[1, 2, 3];
    let _ = a as *const [i32] == b as *const [i32];
}

// === UNDEFINED BEHAVIOR ===

// deref_nullptr
fn test_deref_nullptr() {
    let ptr: *const i32 = std::ptr::null();
    unsafe {
        let _x = *ptr;
    }
}

// drop_bounds
fn test_drop_bounds<T: Drop>(_x: T) {}

// dropping_references
fn test_dropping_references() {
    let x = 5;
    let x_ref = &x;
    unsafe {
        std::ptr::drop_in_place(x_ref as *const i32 as *mut i32);
    }
}

// forgetting_references
fn test_forgetting_references() {
    let x = 5;
    std::mem::forget(&x);
}

// invalid_null_arguments (requires unsafe)
fn test_invalid_null_arguments() {
    unsafe {
        std::ptr::copy_nonoverlapping(std::ptr::null::<i32>(), std::ptr::null_mut::<i32>(), 0);
    }
}

// enum_intrinsics_non_enums
fn test_enum_intrinsics() {
    unsafe {
        let _x = std::mem::discriminant(&5_i32);
    }
}

// === TYPE SAFETY ===

// improper_ctypes
#[repr(C)]
struct BadCStruct {
    field: String,  // String is not FFI-safe
}

extern "C" {
    fn c_function(s: BadCStruct);
}

// improper_ctypes_definitions
#[no_mangle]
pub extern "C" fn improper_ctype_def(s: String) {}

// clashing_extern_declarations
mod a {
    extern "C" {
        fn extern_func(x: i32);
    }
}
mod b {
    extern "C" {
        fn extern_func(x: i64);  // Different signature
    }
}

// missing_abi
extern fn missing_abi_func() {}

// no_mangle_const_items
#[no_mangle]
const CONST_ITEM: i32 = 42;

// repr_c_enums_larger_than_int
#[repr(C)]
enum LargeEnum {
    A = 0x1_0000_0000,
}

// === CONTROL FLOW WARNINGS ===

// while_true
fn test_while_true() {
    while true {
        break;
    }
}

// unused_parens
fn test_unused_parens() {
    let x = (5);
    if (x == 5) {
        println!("five");
    }
}

// unreachable_code
fn test_unreachable_code() {
    return;
    println!("Never executes");
}

// unreachable_patterns
fn test_unreachable_patterns() {
    let x = 5;
    match x {
        _ => println!("catch all"),
        5 => println!("five"),
    }
}

// for_loops_over_fallibles
fn test_for_loops_fallibles() {
    let opt = Some(5);
    for x in opt {
        println!("{}", x);
    }
}

// overlapping_range_endpoints
fn test_overlapping_ranges() {
    let x = 10;
    match x {
        0..=10 => println!("first"),
        10..=20 => println!("second"),
        _ => println!("other"),
    }
}

// === LOGIC ERRORS ===

// unused_must_use
fn returns_result() -> Result<i32, String> {
    Ok(42)
}

fn test_unused_must_use() {
    returns_result();
}

// overflowing_literals
fn test_overflowing_literals() {
    let _x: u8 = 300;
}

// arithmetic_overflow
fn test_arithmetic_overflow() {
    let x: u8 = 255;
    let _y = x + 1;
}

// const_item_mutation
const CONST_ARRAY: [i32; 3] = [1, 2, 3];
fn test_const_item_mutation() {
    let ptr = &CONST_ARRAY as *const [i32; 3] as *mut [i32; 3];
    unsafe {
        (*ptr)[0] = 10;
    }
}

// unused_assignments
fn test_unused_assignments() {
    let mut x = 10;
    x = 20;
}

// noop_method_call
fn test_noop_method_call() {
    let s = String::from("hello");
    let _t = s.clone().clone();
}

// === STYLE IDIOM ===

// non_upper_case_globals
const my_constant: i32 = 42;

// unused_variables
fn test_unused_variables() {
    let unused_var = 42;
}

// dead_code
fn never_called_function() {
    println!("never called");
}

// unused_imports
use std::collections::HashMap;

// === Additional test functions ===

fn test_memory_safety() {
    test_invalid_reference_casting();
    test_static_mut_refs();
    test_invalid_value();
    test_fuzzy_provenance_casts();
    test_lossy_provenance_casts();
    test_ambiguous_wide_pointer();
}

fn test_undefined_behavior() {
    test_deref_nullptr();
    test_dropping_references();
    test_forgetting_references();
    test_invalid_null_arguments();
    test_enum_intrinsics();
}

fn test_type_safety() {
    // Type safety tests are mostly in declarations
}

fn test_control_flow() {
    test_while_true();
    test_unused_parens();
    test_unreachable_code();
    test_unreachable_patterns();
    test_for_loops_fallibles();
    test_overlapping_ranges();
}

fn test_logic_errors() {
    test_unused_must_use();
    test_overflowing_literals();
    test_arithmetic_overflow();
    test_const_item_mutation();
    test_unused_assignments();
    test_noop_method_call();
}

fn test_style_idiom() {
    test_unused_variables();
}
