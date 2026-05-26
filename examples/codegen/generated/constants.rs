// Tooling-compatible constants for Cargo-based workflows.
// Bazel remains the canonical build path and generates equivalent code from templates.

#![allow(dead_code)]
#![allow(clippy::approx_constant)]

/// Project Information
pub mod project {
    pub const NAME: &str = "MyAwesomeProject";
    pub const VERSION: &str = "1.0.0";
    pub const AUTHOR: &str = "Bazel Developer";
}

/// Application Constants
pub mod constants {
    pub const MAX_BUFFER_SIZE: usize = 1024;
    pub const DEFAULT_TIMEOUT: u32 = 30;
    pub const PI: f64 = 3.14159;
    pub const DEBUG: bool = true;
}

/// Messages
pub mod messages {
    pub const WELCOME: &str = "Welcome to the application!";
    pub const ERROR: &str = "An error occurred";
    pub const SUCCESS: &str = "Operation completed successfully";
}

/// Feature Flags
pub mod features {
    pub const LOGGING: bool = true;
    pub const METRICS: bool = false;
    pub const AUTHENTICATION: bool = true;
}

/// Print configuration information
pub fn print_config() {
    println!("Project: {} v{}", project::NAME, project::VERSION);
    println!("Author: {}", project::AUTHOR);
    println!("Debug mode: {}", constants::DEBUG);
    println!(
        "Features: logging={}, metrics={}, auth={}",
        features::LOGGING,
        features::METRICS,
        features::AUTHENTICATION
    );
}
