#pragma once

#include <string>
#include <vector>

class Greeting {
public:
    Greeting(const std::string& name);
    std::string getMessage() const;
    void addArgument(const std::string& arg);
    void printArguments() const;

private:
    std::string name_;
    std::vector<std::string> arguments_;
};