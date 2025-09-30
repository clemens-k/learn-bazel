#include "greeting.h"
#include <iostream>
#include <sstream>

Greeting::Greeting(const std::string& name) : name_(name) {}

std::string Greeting::getMessage() const {
    std::ostringstream oss;
    oss << "Hello, " << name_ << " from C++!";
    return oss.str();
}

void Greeting::addArgument(const std::string& arg) {
    arguments_.push_back(arg);
}

void Greeting::printArguments() const {
    if (!arguments_.empty()) {
        std::cout << "Arguments: ";
        for (size_t i = 0; i < arguments_.size(); ++i) {
            std::cout << arguments_[i];
            if (i < arguments_.size() - 1) {
                std::cout << ", ";
            }
        }
        std::cout << std::endl;
    }
}