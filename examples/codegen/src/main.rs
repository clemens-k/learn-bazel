// Include generated constants library
extern crate rust_constants_lib;

use rust_constants_lib::*;

fn print_messages() {
    println!("\n=== Messages ===");
    println!("Welcome: {}", messages::WELCOME);
    println!("Error: {}", messages::ERROR);
    println!("Success: {}", messages::SUCCESS);
}

fn print_features() {
    println!("\n=== Features ===");
    println!(
        "Logging: {}",
        if features::LOGGING {
            "enabled"
        } else {
            "disabled"
        }
    );
    println!(
        "Metrics: {}",
        if features::METRICS {
            "enabled"
        } else {
            "disabled"
        }
    );
    println!(
        "Authentication: {}",
        if features::AUTHENTICATION {
            "enabled"
        } else {
            "disabled"
        }
    );
}

fn main() {
    println!("Hello from generated Rust code!\n");

    // Use generated configuration
    print_config();
    print_messages();
    print_features();

    println!("\n=== Constants ===");
    println!("Max Buffer Size: {}", constants::MAX_BUFFER_SIZE);
    println!("Default Timeout: {}s", constants::DEFAULT_TIMEOUT);
    println!("Pi: {:.5}", constants::PI);

    if constants::DEBUG {
        println!("\n🐛 Debug mode is enabled!");
    }

    println!("\nThis demonstrates code generation with Bazel!");
}
