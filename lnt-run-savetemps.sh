if [ "$#" -ne 3 ]; then
	echo "run-lnt-emitllvm.sh <sandbox dir> base <core #>"
	echo "run-lnt-emitllvm.sh <sandbox dir> soundimpl <core #>"
	echo "run-lnt-emitllvm.sh <sandbox dir> optimized <core #>"
	exit 1
fi

SANDBOX=$1
$SANDBOX/bin/lnt runtest nt \
      --sandbox $SANDBOX \
      --cc  llvm-${2}-release/bin/clang \
      --cxx llvm-${2}-release/bin/clang++ \
      --test-suite test-suite/ \
      --cflag="-S" --cflag="-save-temps" \
      ${2} -j $3
