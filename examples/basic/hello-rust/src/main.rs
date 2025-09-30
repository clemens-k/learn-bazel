use std::env;
use greeting::Greeting;

fn main() {
    let mut greeting = Greeting::new("Bazel");
    
    println!("{}", greeting.get_message());
    println!("This is my first Rust build with Bazel!");
    
    // Collect command line arguments
    let args: Vec<String> = env::args().skip(1).collect();
    for arg in &args {
        greeting.add_argument(arg);
    }
    
    greeting.print_arguments();
}