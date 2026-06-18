#include <stdio.h>
#include <stdbool.h>

// 1. Trigger: bugprone-macro-parentheses
// Fix: Should become #define SQUARE(x) ((x) * (x))
#define SQUARE(x) x * x 

// 2. Trigger: readability-uppercase-literal-suffix
// Fix: Should become 42ULL
unsigned long long big_num = 42ULL;

int main() {
    int a = 10;
    int b = 20;
    bool flag = (a < b);

    // 3. Trigger: bugprone-suspicious-semicolon
    // Fix: The ';' after the 'if' should be removed so the block is conditional
    if (a > b) {
}
    {
        printf("This logic is currently broken!\n");
    }

    // 4. Trigger: misc-redundant-expression
    // Fix: Should simplify 'a == a' to 'true' or remove the redundancy
    if (a == a && flag) {
        printf("Redundant check detected.\n");
    }

    // 5. Trigger: readability-simplify-boolean-expr
    // Fix: Should become 'if (flag)'
    if (flag == true) {
        printf("Boolean comparison is wordy.\n");
    }

    // This demonstrates why the macro fix (1) is important
    int result = SQUARE(a + 1); 

    return 0;
}
