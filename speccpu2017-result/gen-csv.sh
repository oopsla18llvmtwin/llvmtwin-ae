for i in 1 2 3 ; do
  python2 parse-csv3.py machine${i}/base base${i}.csv llvm-intptr-base-5.0-release
  python2 parse-csv3.py machine${i}/soundimpl temp.csv llvm-intptr-br2-correct2-release
  python2 merge3.py base${i}.csv temp.csv soundimpl${i}.csv
  python2 parse-csv3.py machine${i}/optimized temp.csv llvm-intptr-br5.5-gvnnocast-release
  python2 merge3.py base${i}.csv temp.csv optimized${i}.csv
done
