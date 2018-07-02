import csv
import sys
import os

# returns ( category, benchmark, time, clang dir )
# Note that a single file represents median value of one benchmark.
def parse_csv(filename):
	csvfile = open(filename, 'rb')
	reader = csv.reader(csvfile, delimiter=',')
	
	benchmarkName = None
	elapsedTime = 0.0
	compilerName = ""
	category = None
	if "intrate" in filename:
		category = "CINT2017"
	elif "fprate" in filename:
		category = "CFP2017"
	else:
		assert(False)

	isData = False
	titleExpected = False
	for row in reader:
		if len(row) == 0:
			continue
		if len(row) == 1:
			if row[0] == "Selected Results Table":
				# Begin of data
				assert(not isData)
				isData = True
				titleExpected = True
				continue
			elif row[0].startswith("InstalledDir:"):
				compilerName = row[0][row[0].rfind(":")+1:]
				continue
		if len(row) == 4:
			if row[0] == "SPECrate2017_fp_base" or row[0] == "SPECrate2017_int_base":
				# End of data
				assert(isData)
				isData = False
				continue
		if isData:
			print row
			assert(len(row) == 11 or len(row) == 12)
			if titleExpected:
				assert(row[0] == "Benchmark")
				titleExpected = False
				continue
			assert(row[5] == 'NR' or row[5] == 'S')
			if row[5] == 'S':
				assert(benchmarkName == None)
				benchmarkName = row[0]
				elapsedTime = float(row[2])
	
	compilerName = compilerName.strip()
	if not compilerName.startswith("/mnt/freezedisk/"):
		print compilerName
		assert(compilerName.startswith("/mnt/freezedisk/"))
	compilerName = compilerName[len("/mnt/freezedisk/"):]
	compilerName = compilerName[:(compilerName.find("/"))]
	return (category, benchmarkName, elapsedTime, compilerName)

if len(sys.argv) <> 4 and len(sys.argv) <> 3:
	print "python parse-csv3.py <spec result folder> <output csv> <standard branch(default=llvm-freeze-base-build)>"
	print "python parse-csv3.py <spec result folder> <output csv>"
	exit(1)

specrespath = sys.argv[1]
outputfile = sys.argv[2]
stdbranch="llvm-freeze-base-build"
if len(sys.argv) == 4:
  stdbranch = sys.argv[3]
resulttable = dict() # benchmark -> compiler -> performance
benchmarks = set()
compilers = set()
categories = dict() # category -> benchmark set
for item in os.listdir(specrespath):
	fullpath = specrespath + "/" + item
	if os.path.isdir(fullpath):
		continue
	if not fullpath.endswith("csv"):
		continue
	print fullpath
	# category, benchmark: string
	# elapsedtime: float
	# compiler: string
	(category, benchmark, elapsedtime, compiler) = parse_csv(fullpath)
	if benchmark not in resulttable :
		resulttable[benchmark] = dict()
	if compiler not in resulttable[benchmark]:
		resulttable[benchmark][compiler] = None
	resulttable[benchmark][compiler] = elapsedtime
	benchmarks.add(benchmark)
	compilers.add(compiler)
	print compiler

	if category not in categories:
		categories[category] = set()
	categories[category].add(benchmark)

print compilers

if stdbranch != None and len(compilers) > 1:
  assert(stdbranch in compilers)
else:
  stdbranch = list(compilers)[0]

outputfhandler = open(outputfile, "wb")
writer = csv.writer(outputfhandler)

ckeys = categories.keys()
ckeys.sort()
for category in ckeys:
		writer.writerow([category + "(Itr. 3 times & median taken)"])
		
		benchmarks = list(categories[category])
		benchmarks.sort()
		
		header = ["Benchmark"]
		compilers = list(compilers)
		compilers.remove(stdbranch)
		compilers = [stdbranch] + compilers
		for compiler in compilers:
			header.append(compiler)
			if compiler != stdbranch:
				header.append("Speedup")
				header.append("Slowdown(%)")

		writer.writerow(header)
		for bm in benchmarks:
			row = [bm]
			for compiler in compilers:
				data = resulttable[bm][compiler]
				print bm, compiler, data
				row.append("%.2f" % data)
				if compiler != stdbranch:
					stdval = resulttable[bm][stdbranch]
					row.append("%.6f" % (stdval / data))
					row.append("%.3f" % ((data / stdval - 1) * 100.0))
			writer.writerow(row)
