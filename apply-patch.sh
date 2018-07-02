if [ "$#" -ne 1 ]; then
  echo "apply-patch.sh 1.nointptrfold"
  echo "apply-patch.sh 2.soundimpl"
  echo "apply-patch.sh 3.psub"
  echo "apply-patch.sh 4.optimized"
  echo "apply-patch.sh gvnstat"
  exit 1
fi

dir=`pwd`
cd llvm
git checkout -- .
git clean -f -d
git apply ${dir}/patches/${1}.patch
git apply --stat ${dir}/patches/${1}.patch

cd $dir
cd clang
git checkout -- .
git clean -f -d

if [ "${1}" = "3.psub" ] || [ "${1}" = "4.optimized" ]; then
  git apply ${dir}/patches/3.psub.clang.patch
  git apply --stat ${dir}/patches/3.psub.clang.patch
fi
