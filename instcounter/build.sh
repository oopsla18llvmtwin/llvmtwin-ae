LLVMPATH=../llvm-optimized-release
CXXFLAGS=`$LLVMPATH/bin/llvm-config --cxxflags`
LDFLAGS=`$LLVMPATH/bin/llvm-config --cxxflags --ldflags --libs core interpreter \
    analysis native bitwriter bitreader support transformutils --system-libs`
#LDFLAGS=`../../../llvm-freeze-codegen-build/bin/llvm-config --cxxflags --ldflags --libs --system-libs`
echo "CXXFLAGS:$CXXFLAGS"
echo "LDFLAGS:$LDFLAGS"
echo "========================="
g++ -std=c++11 $CXXFLAGS -c -o instcounter.o instcounter.cpp
echo "========================="
g++ -std=c++11 instcounter.o $LDFLAGS -o instcounter
