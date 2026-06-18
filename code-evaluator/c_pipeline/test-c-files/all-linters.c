#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* readability-identifier-naming */
int BAD_global_NAME = 0;

/* clang-analyzer-core.StackAddressEscape */
int* escape_stack_addr() {
    int local = 42;
    return &local; // returning stack address
}

/* misc-unused-parameters */
int messy_function(int unused_param) {

    /* clang-analyzer-deadcode.DeadStores */
    int x = 5;
    x = 10; // overwritten before use

    /* clang-analyzer-core.UndefinedBinaryOperatorResult */
    int uninit;
    int y = uninit + 1;

    /* bugprone-misplaced-widening-cast */
    short s = (short)y * 1000;

    /* bugprone-unused-return-value + clang-analyzer-unix.Malloc */
    malloc(100); // ignored return + leak

    /* bugprone-sizeof-expression */
    int *ptr = malloc(10 * sizeof(ptr)); // wrong sizeof
    free(ptr);

    /* clang-analyzer-unix.cstring.NullArg */
    char *null_ptr = NULL;
    strlen(null_ptr);

    /* clang-analyzer-unix.cstring.OutOfBounds + insecureAPI.strcpy */
    char small_buf[4];
    strcpy(small_buf, "overflowing string");

    /* bugprone-branch-clone */
    if (y > 0) {
        printf("same\n");
    } else {
        printf("same\n");
    }

    /* custom-goto-statement */
    goto label;

label:
    BAD_global_NAME++;

    /* bugprone-terminating-continue + bugprone-infinite-loop */
    int i = 0;
    while (1) {
        i++;
        continue; // no break possible
    }

    return s;
}

/* bugprone-sizeof-expression (array decay case) */
void array_decay(int arr[]) {
    printf("%zu\n", sizeof(arr)); // pointer size, not array
}

int main() {
    int arr[10];

    /* call everything in one flow */
    int *escaped = escape_stack_addr();
    printf("%p\n", (void*)escaped);

    array_decay(arr);

    messy_function(123);

    return 0;
}
