if [ "$#" -ne 3 ]; then
	echo "run-lnt-emitllvm.sh <sandbox dir> base <core #>"
	echo "run-lnt-emitllvm.sh <sandbox dir> nointptrfold <core #>"
	echo "run-lnt-emitllvm.sh <sandbox dir> soundimpl <core #>"
	echo "run-lnt-emitllvm.sh <sandbox dir> psub <core #>"
	exit 1
fi

SANDBOX=$1
$SANDBOX/bin/lnt runtest nt \
      --sandbox $SANDBOX \
      --cc  llvm-${2}-release/bin/clang \
      --cxx llvm-${2}-release/bin/clang++ \
      --test-suite test-suite/ \
      --cflag="-S" --cflag="-emit-llvm" \
      ${2} -j $3
