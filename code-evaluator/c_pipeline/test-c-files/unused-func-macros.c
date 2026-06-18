#include <stdio.h>

/* --- Macros --- */
// ACTIVE MACRO: Used for logging
#define LOG_INFO(msg) printf("[INFO] %s\n", msg)

// UNUSED MACRO: A complex macro that remains dormant
#define DANGEROUS_CAST(x) ((unsigned int*)(long)(x))

/* --- The Dead Dependency Chain --- */

// Unused Function B: Called by Unused Function A
void internal_logic_helper() {
    // This variable is "used" here, but the function itself is never reached
    int ghost_val = 500;
    printf("Ghost value: %d\n", ghost_val);
}

// Unused Function A: Defines a "weird" edge case
void entry_to_nowhere() {
    LOG_INFO("Attempting to run unreachable logic...");
    internal_logic_helper(); // Function is "used" inside another unused function
}

/* --- Weird Edge Case: The Recursive Zombie --- */
// This function calls itself (recursion), but since it's never 
// called by main, it never triggers a stack overflow or any execution.
void recursive_zombie(int n) {
    if (n > 0) {
        recursive_zombie(n - 1);
    }
}

/* --- The Main Entry Point --- */
int main() {
    // Using the active macro
    LOG_INFO("Starting the engine...");

    // Edge Case: Shadowed unused variable
    // This 'x' is used, but the one defined in the inner scope below is NOT.
    int x = 10;
    
    {
        int x = 20; // Unused shadowed variable
    }

    printf("Active logic: x is %d\n", x);
    LOG_INFO("Process complete.");

    return 0;
}
