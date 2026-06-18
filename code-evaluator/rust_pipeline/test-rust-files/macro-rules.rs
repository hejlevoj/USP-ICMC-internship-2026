// 1. We define the macro using macro_rules!
macro_rules! log_info {
    // Match case 1: Just a simple message
    ($msg:expr) => {
        println!("[INFO] {}", $msg);
    };

    // Match case 2: A message with formatting arguments
    // The `$(...),+` means "match this pattern separated by commas, one or more times"
    ($fmt:expr, $($arg:tt),+) => {
        print!("[INFO] ");
        println!($fmt, $($arg),+);
    };
}

fn main() {
    // Using the macro with a single argument
    log_info!("System started successfully.");

    // Using the macro with multiple formatting arguments
    let user = "Alice";
    let attempts = 3;
    log_info!("User '{}' failed to login after {} attempts.", user, attempts);
}