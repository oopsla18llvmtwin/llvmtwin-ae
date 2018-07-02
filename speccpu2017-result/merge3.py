import csv
import sys
import os

def mergelines(reader1, reader2, writer, N):
  # TITLE
  name1 = reader1.next()
  name2 = reader2.next()
  writer.writerow(name1)

  # BENCHMARKS
  title1 = reader1.next()
  title2 = reader2.next()
  print title1, title2
  reader1name = title1[1]
  reader2name = title2[1]
  title = [title1[0], reader1name, reader2name, "Speedup", "Slowdown(%)"]

  writer.writerow(title)
  for i in range(0, N):
    r1 = reader1.next()
    r2 = reader2.next()
    # rw : 0 ~ 4 column
    data1 = r1[0:2]
    data2 = r2[1:2]
    data = data1 + data2
    med1 = float(data1[1])
    med2 = float(data2[0])
    data.append("%.2f" % (med1 / med2))
    data.append("%.2f" % ((med2 / med1 - 1) * 100))
    writer.writerow(data)

# returns ( category, benchmark, time, clang dir )
def merge_csv(filename1, filename2, fileout):
  csvfile1 = open(filename1, 'rb')
  reader1 = csv.reader(csvfile1, delimiter=',')
  csvfile2 = open(filename2, 'rb')
  reader2 = csv.reader(csvfile2, delimiter=',')
  csvfileout = open(fileout, 'wb')
  writer = csv.writer(csvfileout, delimiter=',')
  mergelines(reader1, reader2, writer, 10) # CFP
  mergelines(reader1, reader2, writer, 9)

if len(sys.argv) <> 4:
  print "python merge.py <input1.csv> <input2.csv> <output csv>"
  exit(1)

merge_csv(sys.argv[1], sys.argv[2], sys.argv[3])
