if [ "$#" -ne 1 ]; then
  echo "count-sum.sh <.bc file aggregated dir(absolute path)>"
  exit 1
fi

BASEDIR=$(dirname "$0")
br=$1
rm count_res.txt
for i in `find ${br} -name "*.bc"` ; do
  echo ${i}
  $BASEDIR/run-instcounter.sh ${i}
done | tee count_res.txt

echo "-------"
for i in "Total" "inttoptr" "ptrtoint" "psub" ; do
printf "${i} "
cat count_res.txt | grep "${i}" | cut -d" " -f2 | awk '{sum+=$1}END{print sum}'
done
