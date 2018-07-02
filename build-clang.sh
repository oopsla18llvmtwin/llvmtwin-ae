if [ "$#" -ne 2 ] ; then
  echo "build-clang.sh base <core # to use>"
  echo "build-clang.sh nointptrfold <core # to use>"
  echo "build-clang.sh soundimpl <core # to use>"
  echo "build-clang.sh psub <core # to use>"
  echo "build-clang.sh optimized <core # to use>"
  echo "build-clang.sh gvnstat <core # to use>"
  exit 1
fi

i=""
if [ "$1" = "base" ] || [ "$1" = "nointptrfold" ] || [ "$1" = "soundimpl" ] || [ "$1" = "psub" ] || [ "$1" = "optimized" ] || [ "$1" = "gvnstat" ]; then
  i=$1
else
  echo "Unknown option : $1"
  exit 2
fi

dir=`pwd`
rm llvm/tools/clang
ln -s ${dir}/clang llvm/tools/clang

target=llvm-${i}-release
mkdir $target
cd $target
if [ "$1" = "gvnstat" ]; then
cmake ${dir}/llvm -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=1 -DLLVM_ENABLE_ASSERTIONS=On
else
cmake ${dir}/llvm -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=1
fi
cmake --build . -- -j$2
