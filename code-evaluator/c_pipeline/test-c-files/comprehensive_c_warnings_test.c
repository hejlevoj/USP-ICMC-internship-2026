// Comprehensive C test file to trigger ALL compiler warnings from c-config.json
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// === CRITICAL SAFETY ===

// -Warray-bounds
void test_array_bounds() {
    int arr[5];
    arr[10] = 42;  // Out of bounds
}

// -Wuse-after-free
void test_use_after_free() {
    int *ptr = malloc(sizeof(int));
    free(ptr);
    *ptr = 10;  // Use after free
}

// -Wdangling-pointer
int* test_dangling_pointer() {
    int x = 5;
    return &x;  // Returns address of local variable
}

// -Wnull-dereference
void test_null_dereference() {
    int *ptr = NULL;
    *ptr = 10;  // Null dereference
}

// -Wrestrict
void test_restrict() {
    char buf[10] = "hello";
    strcpy(buf + 2, buf);  // Overlapping copy
}

// -Wformat-overflow
void test_format_overflow() {
    char buffer[5];
    sprintf(buffer, "This is a very long string");  // Buffer overflow
}

// === LANGUAGE STANDARDS COMPLIANCE ===

// -Wsequence-point
void test_sequence_point() {
    int i = 0;
    i = i++;  // Undefined sequence point
}

// -Wreturn-type
int test_missing_return(int x) {
    if (x > 0) {
        return x;
    }
    // Missing return
}

// -Wuninitialized
void test_uninitialized() {
    int x;
    printf("%d\n", x);  // Uninitialized
}

// -Wstrict-aliasing
void test_strict_aliasing() {
    int i = 5;
    float *f = (float*)&i;  // Strict aliasing violation
    printf("%f\n", *f);
}

// -Wstrict-overflow
void test_strict_overflow(int i) {
    if (i + 1 < i) {  // Assumes signed overflow
        printf("overflow\n");
    }
}

// === DATA INTEGRITY ===

// -Wformat
void test_format() {
    printf("%s", 123);  // Type mismatch
    printf("%d", "string");  // Type mismatch
}

// -Wformat-security
void test_format_security() {
    char *user_input = "test%s%s";
    printf(user_input);  // Format string from user input
}

// -Wsizeof-pointer-div
void test_sizeof_pointer_div() {
    int *arr = malloc(10 * sizeof(int));
    int size = sizeof(arr) / sizeof(int);  // Wrong: dividing pointer size
}

// -Wmemset-transposed-args
void test_memset_transposed() {
    char buf[10];
    memset(buf, sizeof(buf), 0);  // Transposed arguments
}

// -Wconversion
void test_conversion() {
    int i = 300;
    char c = i;  // Implicit conversion with data loss
}

// -Wsign-compare
void test_sign_compare() {
    int signed_val = -1;
    unsigned int unsigned_val = 1;
    if (signed_val < unsigned_val) {
        printf("compare\n");
    }
}

// -Wchar-subscripts
void test_char_subscripts() {
    int arr[10];
    char idx = 5;
    int val = arr[idx];  // Using char as array subscript
}

// === PROGRAM LOGIC ===

// -Wduplicated-cond
void test_duplicated_cond(int x) {
    if (x == 1) {
        printf("one\n");
    } else if (x == 1) {  // Duplicated condition
        printf("also one\n");
    }
}

// -Wduplicated-branches
void test_duplicated_branches(int x) {
    if (x > 0) {
        printf("positive\n");
    } else {
        printf("positive\n");  // Same as if branch
    }
}

// -Wlogical-op
void test_logical_op(int x) {
    if (x < 10 && x < 5) {  // Second condition is redundant
        printf("small\n");
    }
}

// -Wtautological-compare
void test_tautological_compare() {
    unsigned int x = 5;
    if (x >= 0) {  // Always true for unsigned
        printf("non-negative\n");
    }
}

// -Wswitch
void test_switch_missing_case(int x) {
    enum { A, B, C } e;
    switch (e) {
        case A: break;
        case B: break;
        // Missing case C
    }
}

// -Wswitch-enum
enum Color { RED, GREEN, BLUE };
void test_switch_enum(enum Color c) {
    switch (c) {
        case RED: break;
        // Missing GREEN and BLUE
    }
}

// === CONTROL FLOW INTEGRITY ===

// -Wjump-misses-init
void test_jump_misses_init(int flag) {
    if (flag)
        goto skip;
    int x = 10;  // Initialization
skip:
    printf("%d\n", x);
}

// -Wimplicit-fallthrough
void test_implicit_fallthrough(int x) {
    switch(x) {
        case 1:
            printf("one\n");
        case 2:  // Implicit fallthrough
            printf("two\n");
            break;
    }
}

// -Wmultistatement-macros
#define BAD_MACRO(x) printf("%d", x); x++
void test_multistatement_macro() {
    int x = 5;
    if (x > 0)
        BAD_MACRO(x);  // Dangerous with if statement
}

// -Wempty-body
void test_empty_body(int x) {
    if (x > 0);  // Empty body
        printf("positive\n");
}

// === MAINTENANCE AND STYLE ===

// -Wshadow
void test_shadow() {
    int x = 5;
    {
        int x = 10;  // Shadows outer x
        printf("%d\n", x);
    }
}

// -Wparentheses
void test_parentheses(int a, int b, int c) {
    if (a && b || c) {  // Unclear precedence
        printf("match\n");
    }
}

// -Wmissing-braces
void test_missing_braces() {
    int arr[2][2] = {1, 2, 3, 4};  // Missing inner braces
}

// -Wunused-variable
void test_unused_variable() {
    int unused = 10;
}

// -Wignored-qualifiers
const int test_ignored_qualifiers() {  // const on return type is ignored
    return 5;
}

// -Wunused-parameter
void test_unused_parameter(int unused_param) {
    printf("function\n");
}

int main() {
    printf("Testing all C compiler warnings\n");
    return 0;
}
