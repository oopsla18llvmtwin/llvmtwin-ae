import csv
import sys
import os
import json

def get_median (l) : 
  fl = map (float, l)
  fl.sort()
  le = len(fl)
  (a, b) = divmod(le, 2)
  assert(a * 2 + b == le)
  if b == 0:
    return (fl[a] + fl[a - 1]) / 2.0
  return fl[a]

def print_csv(rtcsv_outputname, execresult, benchmarks, clangs) :
  fptr = open(rtcsv_outputname, "wb")
  writer = csv.writer(fptr)
  body = []
  # trials : clangname -> int
  trials = dict()
  # fails : clangname -> int
  fails = dict()
  # sums : clangname -> float
  sums = dict()
  for cl in clangs:
    sums[cl] = 0.0
    fails[cl] = 0

  for bm in benchmarks:
    thisrow = []
    thisrow.append(bm)
    brdict = execresult[bm]
    for cl in clangs:
      timelist = brdict[cl]
      thisrow = thisrow + timelist
      failed = False
      for t in timelist : 
        try:
          float(t)
        except ValueError : 
          failed = True
          break
      if failed:
        thisrow.append("-")
        fails[cl] = fails[cl] + 1
      else:
        thisrow.append(get_median(timelist))
        sums[cl] = sums[cl] + get_median(timelist)

      if cl in trials:
        assert(trials[cl] == len(timelist))
      else:
        trials[cl] = len(timelist)
    body.append(thisrow)

  header = ["Benchmarks"]
  footer = ["Total elapsed time"]
  footer2 = ["Total failure"]
  for cl in clangs:
    for i in range(0, trials[cl]) :
      header.append(cl)
      footer.append("-")
      footer2.append("-")
    header.append("median")
    footer.append(sums[cl])
    footer2.append(fails[cl])
  writer.writerow(header)
  writer.writerows(body)
  writer.writerow(footer)
  writer.writerow(footer2)

# python parse.py <lntdir> <compiletime-outputcsv> <runtime-outputcsv>
if len(sys.argv) != 4 :
  print "python parse.py <mysandbox dir> <compiletime-output.csv> <runningtime-output.csv>"
  exit(0)

mysandboxdir = sys.argv[1]
cccsv_outputname = sys.argv[2]
rtcsv_outputname = sys.argv[3]

# result : benchmark -> branch -> ((elapsed time or string) list)
execresult = dict()
ccresult = dict()
clangs = []

empty = True
ld = os.listdir(mysandboxdir)
ld.sort()
for eachpath in ld :
  if not eachpath.startswith("test-") :
    continue
  empty = False
  print eachpath
  # step 1. get clang dir
  infojson = json.load(open(mysandboxdir + "/" + eachpath + "/report.json"))
  clangpath = infojson["Run"]["Info"]["TARGET_LLVMGCC"]
  print clangpath
  clangs.append(clangpath)
  # step 2. read report.simple.csv
  reportf = open(mysandboxdir + "/" + eachpath + "/report.simple.csv")
  reportcsv = csv.reader(reportf, delimiter=',')

  isHeader = True
  for eachrow in reportcsv:
    if isHeader:
      isHeader = False
      continue

    benchmark = eachrow[0]
    if benchmark not in execresult :
      execresult[benchmark] = dict()
    if benchmark not in ccresult :
      ccresult[benchmark] = dict()

    if clangpath not in execresult[benchmark] :
      execresult[benchmark][clangpath] = []
    if clangpath not in ccresult[benchmark] : 
      ccresult[benchmark][clangpath] = []
    
    # 'cc' column check!
    if eachrow[1] == "pass" : 
      # I used CC_Real_Time.
      ccresult[benchmark][clangpath].append(eachrow[3])
      # 'exec' column check!
      if eachrow[5] == "pass" :
        execresult[benchmark][clangpath].append(eachrow[7])
      else:
        # if not "pass", then what else?
        execresult[benchmark][clangpath].append(eachrow[5])
    else:
      # if not "pass" then what else?
      ccresult[benchmark][clangpath].append(eachrow[1])
      execresult[benchmark][clangpath].append("")

if empty:
  print "The folder has no 'test-*' subdirectories!"
  exit(1)

clangs = list(set(clangs))
clangs.sort()
benchmarks = execresult.keys()
benchmarks.sort()
print_csv(rtcsv_outputname, execresult, benchmarks, clangs)
print_csv(cccsv_outputname, ccresult, benchmarks, clangs)
