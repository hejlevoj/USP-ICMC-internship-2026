// This will compile, but it's going to be a sea of yellow text.

use std::collections::HashMap;

// Compiler Warning: Non-snake-case naming
fn BadNamingConvention(X: i32) -> i32 {
    // Clippy Warning: Manual implementation of something that exists
    // (e.g., adding 0 or multiplying by 1)
    let y = X + 0;
    
    // Compiler Warning: Unused variable
    let unused_var = 50;

    y
}

fn main() {
    // Clippy Warning: Using `format!` when a simple string would do
    let s = format!("just a string");
    println!("{}", s);

    // Clippy Warning: Complex redundancy (approx_constant)
    let pi = 3.14159; 

    // Clippy Warning: Identity conversion
    let value = 10;
    let _ = value.to_owned();

    let result = BadNamingConvention(5);

    // Compiler Warning: Unreachable code
    return;
    println!("This will never print, and the compiler knows it!");
}
