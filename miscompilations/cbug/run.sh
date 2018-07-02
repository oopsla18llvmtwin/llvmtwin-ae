echo "-------------------------------------------------"
echo "Correct answer: either a=100, x=0 or a=0, x=15"
echo "-------------------------------------------------"

for cc in gcc "../../llvm-base-release/bin/clang" "../../llvm-soundimpl-release/bin/clang" \
          "../../llvm-optimized-release/bin/clang"; do
  echo "- Running ${cc}.."
  ${cc} -O3 a.c b.c -o a
  ./a
  echo "- Running ${cc} (with variables x, y reordered, should be correct too).."
  ${cc} -O3 a2.c b.c -o a
  ./a
done
rm a
