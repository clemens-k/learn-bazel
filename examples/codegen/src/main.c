#include <stdio.h>
#include "config.h"

void print_config(void) {
    printf("=== Configuration ===\n");
    printf("Project: %s v%s\n", PROJECT_NAME, PROJECT_VERSION);
    printf("Author: %s\n", PROJECT_AUTHOR);
    printf("Max Buffer Size: %d\n", MAX_BUFFER_SIZE);
    printf("Default Timeout: %d\n", DEFAULT_TIMEOUT);
    printf("Pi: %.5f\n", PI);
    printf("Debug: %s\n", DEBUG ? "true" : "false");
}

void print_messages(void) {
    printf("\n=== Messages ===\n");
    printf("Welcome: %s\n", MSG_WELCOME);
    printf("Error: %s\n", MSG_ERROR);
    printf("Success: %s\n", MSG_SUCCESS);
}

void print_features(void) {
    printf("\n=== Features ===\n");
    printf("Logging: %s\n", FEATURE_LOGGING ? "enabled" : "disabled");
    printf("Metrics: %s\n", FEATURE_METRICS ? "enabled" : "disabled");
    printf("Authentication: %s\n", FEATURE_AUTHENTICATION ? "enabled" : "disabled");
}

int main() {
    printf("Hello from generated C code!\n\n");
    
    print_config();
    print_messages();
    print_features();
    
    printf("\nThis demonstrates code generation with Bazel!\n");
    return 0;
}