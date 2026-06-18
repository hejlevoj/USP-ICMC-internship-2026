#include <stdio.h>
#define MAX_VAL 100 // This is used
#define UNUSED_VAL 500  /* Why is this here? Nobody knows */
#define MULTIPLY(a,b) (a*b)
#define TRIPLE_UNUSED(x) (x*3) 

// Global variable because why not
int global_count = 0;

void thisFunctionIsNeverCalled(int x){
printf("I am a ghost in the machine... %d\n", x);
    for(int i=0;i<10;i++){
        global_count++;
}}

int main(){
int a=5;int b=10;
    // Starting the main logic now
if(a<b){
printf("A is smaller\n");
    }else{
                printf("B is smaller or equal\n");
}
    
    /* * We should probably calculate something here 
     * but instead I'll just print a macro result
     */
    printf("Result: %d\n", MULTIPLY(a, b));

return 0;
    // Logic ends here... I think?
}

float anotherUnusedFunction(float f){
            float result = f * 2.5f;
    return result;
}

// Final comment: This code is a disaster.
