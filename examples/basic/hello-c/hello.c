#include <stdio.h>
#include <stdlib.h>

int main(int argc, char* argv[]) {
    printf("Hello, Bazel from C!\n");
    printf("This is my first C build with Bazel!\n");
    
    if (argc > 1) {
        printf("Arguments: ");
        for (int i = 1; i < argc; i++) {
            printf("%s ", argv[i]);
        }
        printf("\n");
    }
    
    return 0;
}