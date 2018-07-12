if [ "$#" -ne 3 ] ; then
  echo "build-llvm.sh <LLVM dir (absolute path)> <LLVM install dir> <# of cores>"
  exit 1
fi

mkdir $2
cd $2
cmake $1 -DCMAKE_BUILD_TYPE=Release #-DBUILD_SHARED_LIBS=1
cmake --build . -- -j$3
