use std::env;
use std::path::PathBuf;
use std::process::Command;

fn main() {
    println!("cargo:rerun-if-changed=config.yaml");
    println!("cargo:rerun-if-changed=generate.py");
    println!("cargo:rerun-if-changed=templates/constants.rs.j2");

    let manifest_dir =
        PathBuf::from(env::var("CARGO_MANIFEST_DIR").expect("CARGO_MANIFEST_DIR must be set"));
    let out_dir = PathBuf::from(env::var("OUT_DIR").expect("OUT_DIR must be set"));
    let output_file = out_dir.join("constants.rs");
    let generator_script = manifest_dir.join("generate.py");
    let config_file = manifest_dir.join("config.yaml");
    let template_file = manifest_dir.join("templates/constants.rs.j2");

    let status = Command::new("python3")
        .arg(
            generator_script
                .to_str()
                .expect("generator_script path must be valid UTF-8"),
        )
        .args([
            "rust",
            config_file
                .to_str()
                .expect("config_file path must be valid UTF-8"),
            template_file
                .to_str()
                .expect("template_file path must be valid UTF-8"),
            output_file
                .to_str()
                .expect("output_file path must be valid UTF-8"),
        ])
        .status()
        .expect("failed to execute `python3 generate.py`");

    assert!(
        status.success(),
        "generate.py failed (status: {status}). Ensure `python3` and `pyyaml` are installed."
    );
}
