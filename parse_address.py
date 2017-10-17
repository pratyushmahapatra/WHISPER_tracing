#!/usr/bin/env python-3.5.2
import sys, getopt

pinfile = ''
tracefile = ''
outputfile = ''

try:
   opts, args = getopt.getopt(sys.argv[1:],"hp:t:o:",["ifile=","ofile="])
except getopt.GetoptError:
   print 'parse_address.py -p <pinfile> -t <tracefile> -o <outputfile>'
   sys.exit(2)

for opt, arg in opts:
   if opt == '-h':
      print 'parse_address.py -p <pinfile> -t <tracefile> -o <outputfile>'
      sys.exit()
   elif opt in ("-p", "--pfile"):
      pinfile = arg
   elif opt in ("-t", "--tfile"):
      tracefile = arg
   elif opt in ("-o", "--tfile"):
      outputfile = arg


pinatrace = open(pinfile, "r")

pc_value_pm_accesses = []

pc_value_pm_accesses = pinatrace.readlines()
pinatrace.close()

del pc_value_pm_accesses[-1]
del pc_value_pm_accesses[0:3]

i=0
total = 0
pin_pc = {}       # address -> {pc}
pin_occ = {}      # pc -> {occurence}
pin_addr = {}
pin_addr = set() 
for lines in pc_value_pm_accesses:
	lines = lines.split(' ')
	try:
		del lines[5]
	except IndexError:
		pass 
	del lines[3:5]
	del lines[1]
	addr = int(lines[1],0)
	pc = int(lines[0][:-1],0)
	pin_pc[addr] = pc 
	pin_occ[pc] = 0
	pc_value_pm_accesses[i] = pc
	pin_addr.add(addr) 
	i = i + 1


for pc in pc_value_pm_accesses:
	pin_occ[pc] += 1


tracefile = open(tracefile, "r")
traceread = []
traceread = tracefile.readlines()
tracefile.close()


del traceread[0:11]
trace_addr = {}
trace_addr = set()
for lines in traceread:
	lines = lines.split(":")
	try:
		if "0x" in lines[3]:
			trace_addr.add(int(lines[3],0))
	except IndexError:
		continue

pin_addr = pin_addr.difference(trace_addr)

pin_pc_set = {}
pin_pc_set = set()

for addr in pin_addr:
	pin_pc_set.add(pin_pc[addr])
	
pin_occ_list = []
pin_pc_list = []

for pc in pin_pc_set:
	pin_pc_list.append(pc)
	pin_occ_list.append(pin_occ[pc])

pin_occ_list, pin_pc_list = zip(*sorted(zip(pin_occ_list, pin_pc_list), reverse=True))

pc_file = open(outputfile, "w")
pc_file.write("PC Value     :  Number of Accesses\n")
total = 0

for n in pin_pc_list:
	pc_file.write("0x%0x       :   %d\n" %(n, pin_occ[n]))
	total += pin_occ[n]	 

pc_file.write("Total number of accesses : %d" %total)
pc_file.close()

