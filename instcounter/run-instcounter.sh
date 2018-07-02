BASEDIR=$(dirname "$0")
export LD_LIBRARY_PATH=${BASEDIR}/../llvm-optimized-release/lib
$BASEDIR/instcounter $@
