// Test file to trigger all GCC warning categories
// Categories: memory_safety, undefined_behavior, type_safety, control_flow, logic_errors, style_idiom

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

// MEMORY_SAFETY warnings

// -Warray-bounds
void test_array_bounds() {
    int arr[5];
    arr[10] = 42;  // Out of bounds access
}

// -Wnull-dereference
void test_null_deref() {
    int *ptr = NULL;
    *ptr = 42;  // Null pointer dereference
}

// -Wformat-overflow
void test_format_overflow() {
    char buf[5];
    sprintf(buf, "This is a very long string that will overflow");
}

// -Wrestrict
void test_restrict() {
    char str[] = "hello";
    strcpy(str, str + 2);  // Overlapping memory
}

// UNDEFINED_BEHAVIOR warnings

// -Wsequence-point
int test_sequence_point() {
    int i = 0;
    return i++ + i++;  // Undefined sequence point
}

// -Wreturn-type
int test_missing_return() {
    int x = 5;
    // Missing return statement
}

// -Wuninitialized
int test_uninitialized() {
    int x;
    return x + 5;  // Using uninitialized variable
}

// -Wstrict-aliasing
void test_strict_aliasing() {
    int x = 42;
    float *f = (float *)&x;  // Type-punning
    *f = 3.14f;
}

// -Wimplicit-function-declaration
// Note: With -std=c17, implicit declarations are errors, not warnings
// This test is omitted to allow compilation
void test_implicit_function() {
    // Implicit function declarations are compilation errors in C17
    // Skip this test
}

// -Wstrict-overflow
void test_strict_overflow(int x) {
    if (x + 1 < x) {  // Assuming overflow
        printf("overflow\n");
    }
}

// TYPE_SAFETY warnings

// -Wformat and -Wformat-security
void test_format_issues() {
    int x = 42;
    printf("%s", x);  // Wrong format specifier

    char *user_input = "user data";
    printf(user_input);  // Format security issue
}

// -Wchar-subscripts
void test_char_subscripts() {
    int arr[10];
    char c = 'a';
    int val = arr[c];  // Using char as array subscript
}

// -Wconversion and -Wsign-compare
void test_conversions() {
    unsigned int u = 10;
    int s = -5;
    if (s < u) {  // Signed vs unsigned comparison
        printf("compare\n");
    }

    long long big = 1234567890123LL;
    int small = big;  // Lossy conversion
}

// CONTROL_FLOW warnings

// -Wimplicit-fallthrough
void test_fallthrough(int x) {
    switch (x) {
        case 1:
            printf("one\n");
            // Missing break - implicit fallthrough
        case 2:
            printf("two\n");
            break;
    }
}

// -Wjump-misses-init
void test_jump_init(int flag) {
    if (flag)
        goto skip;
    int x = 42;  // Initialization skipped by goto
skip:
    printf("%d\n", x);
}

// -Wswitch
void test_switch_incomplete(int x) {
    enum {A, B, C} e = A;
    switch (e) {
        case A:
            break;
        // Missing cases B and C
    }
}

// -Wempty-body
void test_empty_body(int x) {
    if (x > 0);  // Empty body
        printf("positive\n");
}

// LOGIC_ERRORS warnings

// -Wduplicated-cond
void test_duplicated_cond(int x) {
    if (x > 0) {
        printf("positive\n");
    } else if (x > 0) {  // Duplicated condition
        printf("also positive?\n");
    }
}

// -Wduplicated-branches
void test_duplicated_branches(int x) {
    if (x > 0) {
        printf("value\n");
    } else {
        printf("value\n");  // Identical branches
    }
}

// -Wlogical-op
void test_logical_op(int x) {
    if (x < 0 || x < 10) {  // Suspicious logical OR
        printf("test\n");
    }
}

// -Wsizeof-pointer-div
void test_sizeof_pointer_div() {
    int *arr = malloc(10 * sizeof(int));
    int count = sizeof(arr) / sizeof(int);  // Wrong: sizeof pointer, not array
}

// -Wmemset-transposed-args
void test_memset_transposed() {
    char buf[100];
    memset(buf, sizeof(buf), 0);  // Arguments transposed
}

// STYLE_IDIOM warnings

// -Wshadow
int global_var = 10;
void test_shadow() {
    int global_var = 20;  // Shadows global variable
    printf("%d\n", global_var);
}

// -Wparentheses
void test_parentheses(int a, int b, int c) {
    if (a && b || c) {  // Confusing precedence
        printf("test\n");
    }
}

// -Wmissing-braces
void test_missing_braces() {
    int arr[2][2] = {1, 2, 3, 4};  // Missing inner braces
}

// -Wunused-variable and -Wunused-parameter
void test_unused(int unused_param) {
    int unused_var = 42;
    printf("test\n");
}

// -Wignored-qualifiers
const int test_ignored_qualifiers() {
    return 42;  // const on return type is ignored
}

int main() {
    printf("This file is designed to trigger GCC warnings, not to run correctly.\n");
    return 0;
}
