#![allow(dead_code)]
#![allow(unused_variables)]
#![allow(invalid_reference_casting)]

use std::mem;

/* ===== TRAIT / IMPL ===== */
trait MyTrait {
    fn do_something(&self) -> i32;
}

struct MyStruct {
    pub value: i32,
}

impl MyTrait for MyStruct {
    fn do_something(&self) -> i32 {
        let x = self.value;
        return x; // clippy::let_and_return
    }
}

/* ===== DEFAULT REASSIGN ===== */
#[derive(Default)]
struct Config {
    a: i32,
    b: i32,
}

/* ===== MEMORY LINTS ===== */
fn deref_raw(p: *const i32) -> i32 {
    unsafe { *p } // clippy::not_unsafe_ptr_arg_deref
}

fn mut_from_ref(x: &i32) -> &mut i32 {
    unsafe { &mut *(x as *const i32 as *mut i32) } // clippy::mut_from_ref
}

unsafe fn pointer_casts() {
    let x = 5u32;
    let p1 = &x as *const u32 as *const u8; // ptr_as_ptr
    let p2 = p1 as *const u32; // cast_ptr_alignment

    unsafe {
        let _r = &*p2; // invalid_reference_casting
    }
}

unsafe fn transmute_example() {
    let x = 10u32;
    let p = &x as *const u32;

    unsafe {
        let _q: *const u8 = mem::transmute(p); // transmute_ptr_to_ptr
    }
}

fn undocumented_unsafe() {
    unsafe {
        let x = 5;
        let p = &x as *const i32;
        println!("{}", *p); // undocumented_unsafe_blocks
    }
}

/* ===== CONTROL FLOW ===== */
fn loop_issues() {
    let v = vec![1, 2, 3];

    for i in 0..v.len() { // needless_range_loop
        println!("{}", v[i]);
    }

    let mut counter = 0;
    for x in &v {
        println!("{} {}", counter, x); // explicit_counter_loop
        counter += 1;
    }
}

fn iterator_issue() {
    let v = vec![1, 2, 3];
    let mut it = v.iter();

    while let Some(x) = it.next() { // while_let_on_iterator
        println!("{}", x);
    }
}

fn manual_iterators() {
    let v = vec![Some(1), None, Some(3)];

    let mut flat = Vec::new();
    for x in v {
        if let Some(val) = x { // manual_flatten
            flat.push(val);
        }
    }

    let nums = vec![1, 2, 3, 4];

    let mut found = None;
    for n in &nums { // manual_find
        if *n == 3 {
            found = Some(n);
            break;
        }
    }

    let mut mapped = Vec::new();
    for n in &nums { // manual_map
        mapped.push(n * 2);
    }

    let mut filtered = Vec::new();
    for n in &nums { // manual_filter
        if *n % 2 == 0 {
            filtered.push(n);
        }
    }
}

/* ===== MUTATION ===== */
fn needless_mut() {
    let mut x = 5; // needless_mut
    println!("{}", x);
}

unsafe fn ptr_offset_issue() {
    let arr = [1, 2, 3];
    let p = arr.as_ptr();
    let _ = (p as usize + 1) as *const i32; // ptr_offset_with_cast
}

fn manual_copy() {
    let src = [1, 2, 3];
    let mut dst = [0; 3];

    for i in 0..3 { // manual_memcpy
        dst[i] = src[i];
    }
}

fn collect_issue() {
    let v = vec![1, 2, 3];

    let sum: i32 = v
        .iter()
        .collect::<Vec<_>>() // needless_collect
        .iter()
        .copied()
        .sum();

    println!("{}", sum);
}

/* ===== IDIOMATIC ===== */
fn clone_issues() {
    let x = 5;
    let _y = x.clone(); // clone_on_copy

    let s = String::from("hello");
    let t = s.clone(); // redundant_clone

    let r = &t;
    println!("{}", &r); // needless_borrow
}

/* ===== EXTRA KEYWORDS ===== */
fn advanced_features() {
    let f: Box<dyn Fn(i32) -> i32> = Box::new(|x| x + 1);

    let closure = move |x: i32| x * 2;

    fn generic<T>(x: T) -> T
    where
        T: Copy,
    {
        x
    }

    println!("{}", f(2));
    println!("{}", closure(3));
}

/* ===== MAIN ===== */
fn main() {
    let mut cfg = Config::default();
    cfg.a = 10; // field_reassign_with_default

    let s = MyStruct { value: 42 };
    println!("{}", s.do_something());

    let x = 5;
    println!("{}", deref_raw(&x));

    unsafe {
        pointer_casts();
        transmute_example();
        ptr_offset_issue();
    }

    mut_from_ref(&x);

    undocumented_unsafe();
    loop_issues();
    iterator_issue();
    manual_iterators();
    needless_mut();
    manual_copy();
    collect_issue();
    clone_issues();
    advanced_features();
}
