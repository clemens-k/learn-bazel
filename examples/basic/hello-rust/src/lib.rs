//! A simple greeting library demonstrating Rust with Bazel

pub struct Greeting {
    name: String,
    arguments: Vec<String>,
}

impl Greeting {
    /// Create a new greeting with the given name
    pub fn new(name: &str) -> Self {
        Self {
            name: name.to_string(),
            arguments: Vec::new(),
        }
    }

    /// Get the greeting message
    pub fn get_message(&self) -> String {
        format!("Hello, {} from Rust!", self.name)
    }

    /// Add an argument to the greeting
    pub fn add_argument(&mut self, arg: &str) {
        self.arguments.push(arg.to_string());
    }

    /// Print all arguments
    pub fn print_arguments(&self) {
        if !self.arguments.is_empty() {
            println!("Arguments: {}", self.arguments.join(", "));
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_greeting() {
        let greeting = Greeting::new("Bazel");
        assert_eq!(greeting.get_message(), "Hello, Bazel from Rust!");
    }

    #[test]
    fn test_arguments() {
        let mut greeting = Greeting::new("Test");
        greeting.add_argument("arg1");
        greeting.add_argument("arg2");
        assert_eq!(greeting.arguments.len(), 2);
    }
}