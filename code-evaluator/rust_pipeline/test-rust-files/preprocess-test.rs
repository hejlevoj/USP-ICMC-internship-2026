#![allow(unused_variables)]
#![allow(dead_code)]
#![allow(unused_imports)]

use std::collections::HashMap; 

// --- TRAIT DEFINITION ---
pub        trait      UselessTrait {
    fn     do_nothing(&self);
}

// --- STRUCT DEFINITION ---
    pub struct     MessyData {
pub    field: Option<i32>
    }

// --- THE IMPLEMENTATION ---
impl UselessTrait for MessyData {
             fn do_nothing(&self) {
        let x = 5;
                    let y = 10;
    }
}

            fn        this_is_never_called(mut       a: i32) {
    let      b = 20; 
            let c = "unformatted string";
                if a > b {
        if b < 100 {
match Some(a) {
    Some(val) => {
println!("Deep nesting for fun: {}", val);
    }
            None => {   }
}
        }
    }
}

fn random_math_commented(ref_val: &i32) -> i32 {
    /* Multi-line comment 
       in the middle 
    */
    let result = *ref_val + 10;
            result
}

fn main() {
    // We instantiate the struct
    let    data = MessyData { field: Some(42) };
    
    // We call the trait method (this requires UselessTrait to be in scope)
    data.do_nothing();

    let    mut    x = 5;
    let y = &mut x;
        *y += 1;
    
            println!("Done.");
}

// trailing comment
