#include "greeting.h"
#include <iostream>

int main(int argc, char* argv[]) {
    Greeting greeting("Bazel");
    
    std::cout << greeting.getMessage() << std::endl;
    std::cout << "This is my first C++ build with Bazel!" << std::endl;
    
    // Add command line arguments to greeting
    for (int i = 1; i < argc; ++i) {
        greeting.addArgument(argv[i]);
    }
    
    greeting.printArguments();
    
    return 0;
}