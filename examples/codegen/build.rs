use std::env;
use std::path::PathBuf;
use std::process::Command;

fn main() {
    println!("cargo:rerun-if-changed=config.yaml");
    println!("cargo:rerun-if-changed=generate.py");
    println!("cargo:rerun-if-changed=templates/constants.rs.j2");

    let out_dir = PathBuf::from(env::var("OUT_DIR").expect("OUT_DIR must be set"));
    let output_file = out_dir.join("constants.rs");

    let status = Command::new("python3")
        .args([
            "generate.py",
            "rust",
            "config.yaml",
            "templates/constants.rs.j2",
            output_file
                .to_str()
                .expect("output_file path must be valid UTF-8"),
        ])
        .status()
        .expect("failed to execute python3 generate.py");

    assert!(
        status.success(),
        "generate.py failed with status: {status}"
    );
}
