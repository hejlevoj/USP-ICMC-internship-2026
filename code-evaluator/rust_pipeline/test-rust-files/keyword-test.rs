use std::collections::HashMap;

macro_rules! my_macro {
    ($x:expr) => {
        println!("{}", $x);
    };
}

fn helper(val: &i32) -> i32 {
    *val + 1
}

fn main() {
    let mut x = 5;
    let result = helper(&x);
    let map: HashMap<String, i32> = HashMap::new();
    let _ = map;
    my_macro!("hello");
    if result > 3 {
        panic!("too big");
    }
    unsafe {
        let ptr = &mut x as *mut i32;
        *ptr = 10;
    }
    println!("done: {}", x);
}
