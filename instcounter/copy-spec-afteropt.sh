if [ "$#" -ne 2 ]; then 
  echo "copy-spec-afteropt.sh <destination dir (absolute path)> <SPEC dir (absolute path)>"
  exit 1
fi

TARGDIR=$1
DIRID=$2

for BENCHMARK in \
    500.perlbench_r  502.gcc_r 505.mcf_r 520.omnetpp_r \
    523.xalancbmk_r 525.x264_r 531.deepsjeng_r   541.leela_r \
    557.xz_r 508.namd_r 510.parest_r 511.povray_r 519.lbm_r \
    526.blender_r 538.imagick_r 544.nab_r \
    507.cactuBSSN_r 521.wrf_r 527.cam4_r; do
  cd ${DIRID}/benchspec/CPU/${BENCHMARK}/build
  echo $BENCHMARK
  dirname=`ls -td -- */ | head -n 1`
  echo $dirname
  mkdir $TARGDIR/$BENCHMARK
  
  cd $dirname
  for i in `find . -name "*.o"`; do
    fty=`file ${i} | cut -d' ' -f2`
    if [ "$fty" == "ASCII" ]; then
      echo ${i}
      echo $TARGDIR/$BENCHMARK
      cp --parents ${i} $TARGDIR/$BENCHMARK
    fi
  done
  cd ..
done
