rm -rf target
echo $PATH
export PATH=/home/oopsla18/llvmtwin-ae/rust-patched-install/bin:$PATH
echo "Correct output: c = 0, x = 7777 and c = 1, x = 42."
echo not optimized:
cargo run
echo
echo optimized:
cargo run --release
