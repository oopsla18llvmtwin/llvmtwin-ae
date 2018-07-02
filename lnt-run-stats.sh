if [ "$#" -ne 2 ]; then
	echo "run-lnt-stats.sh <sandbox dir> <core #>"
	exit 1
fi

SANDBOX=$1
$SANDBOX/bin/lnt runtest nt \
      --sandbox $SANDBOX \
      --cc  llvm-gvnstat-release/bin/clang \
      --cxx llvm-gvnstat-release/bin/clang++ \
      --test-suite test-suite/ \
      --cflag="-mllvm" --cflag="-stats" \
      gvnstats -j $2
