














#![allow(unused_variables, dead_code)]

fn main() {
    // clippy::approx_constant
    let pi = 3.14;

    // clippy::unnecessary_allocation
    let my_string = "hello".to_string().to_string();

    // clippy::len_zero
    let my_vec = vec![1, 2, 3];
    if my_vec.len() == 0 {
        println!("Empty!");
    }

    // clippy::comparison_to_empty
    let empty_str = "";
    if empty_str == "" {
        println!("It is empty");
    }

    // clippy::needless_bool
    let is_greater = if 10 > 5 { true } else { false };

    // clippy::single_match
    let some_option = Some(42);
    match some_option {
        Some(x) => println!("Value: {}", x),
        None => (),
    }

    println!("Pi: {}, Greater: {}", pi, is_greater);
}
