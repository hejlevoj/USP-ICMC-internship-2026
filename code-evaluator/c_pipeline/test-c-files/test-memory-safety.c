// Test file specifically for memory_safety warnings
// Target warnings: -Warray-bounds, -Wuse-after-free, -Wdangling-pointer,
//                  -Wnull-dereference, -Wformat-overflow, -Wrestrict

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

// -Warray-bounds
void test_array_bounds_1() {
    int arr[5];
    arr[5] = 10;  // Out of bounds (index 5 in array of size 5)
    arr[10] = 20; // Far out of bounds
}

void test_array_bounds_2() {
    char buf[10];
    buf[15] = 'x';  // Out of bounds
}

// -Wuse-after-free
void test_use_after_free() {
    int *ptr = malloc(sizeof(int));
    free(ptr);
    *ptr = 42;  // Use after free
}

void test_use_after_free_2() {
    char *str = malloc(100);
    free(str);
    strcpy(str, "hello");  // Use after free
}

// -Wdangling-pointer
int* test_dangling_pointer_1() {
    int local = 42;
    return &local;  // Returning address of local variable
}

char* test_dangling_pointer_2() {
    char buffer[100];
    return buffer;  // Returning address of local array
}

void test_dangling_pointer_3() {
    int *ptr;
    {
        int scoped = 10;
        ptr = &scoped;
    }
    *ptr = 20;  // Using pointer to out-of-scope variable
}

// -Wnull-dereference
void test_null_deref_1() {
    int *ptr = NULL;
    *ptr = 42;  // Direct null dereference
}

void test_null_deref_2(int *p) {
    if (p == NULL) {
        *p = 10;  // Dereference after null check
    }
}

void test_null_deref_3() {
    int *ptr = 0;
    int x = *ptr + 5;  // Dereference of null
}

// -Wformat-overflow
void test_format_overflow_1() {
    char buf[5];
    sprintf(buf, "This is a very long string");  // Buffer overflow
}

void test_format_overflow_2() {
    char small[4];
    snprintf(small, sizeof(small), "%d %d %d %d", 1, 2, 3, 4);  // Overflow
}

void test_format_overflow_3() {
    char tiny[2];
    sprintf(tiny, "%d", 12345);  // Number too large for buffer
}

// -Wrestrict
void test_restrict_1() {
    char str[20] = "hello";
    strcpy(str, str + 2);  // Overlapping source and dest
}

void test_restrict_2() {
    char buffer[30] = "test";
    strcat(buffer, buffer);  // Self-concatenation
}

void test_restrict_3() {
    char data[50] = "data";
    sprintf(data, "%s world", data);  // Overlapping format and argument
}

// Combined tests
void test_multiple_issues() {
    int arr[3];
    arr[-1] = 0;   // Negative index (array-bounds)
    arr[3] = 1;    // Out of bounds (array-bounds)

    char buf[8];
    sprintf(buf, "overflow test string");  // format-overflow

    int *null_ptr = NULL;
    if (null_ptr) {
        // Logic issue
    } else {
        *null_ptr = 100;  // null-dereference in else branch
    }

    char *freed = malloc(20);
    free(freed);
    freed[0] = 'x';  // use-after-free
}

int main() {
    printf("Memory safety test - not meant to run, only to compile with warnings\n");
    return 0;
}
