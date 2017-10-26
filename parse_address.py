#!/usr/bin/env python-3.5.2
import sys, getopt

pinfile = ''
tracefile = ''
outputfile = ''
exefile = ''
r_w = ''
d_i = 0;

try:
   opts, args = getopt.getopt(sys.argv[1:],"hp:t:o:e:a:d:",["pfile=","tfile=","ofile="])
except getopt.GetoptError:
   print 'parse_address.py -p <pinfile> -t <tracefile> -o <outputfile> -e <executable file> -a <R/W> -d <diff(0) or intersection(1)>'
   sys.exit(2)

for opt, arg in opts:
	if opt == '-h':
		print 'parse_address.py -p <pinfile> -t <tracefile> -o <outputfile> -e <executable file> -a <read(R) or write(W)> -d <diff(0) or intersection(1)>'
		sys.exit()
	elif opt in ("-p", "--pfile"):
		pinfile = arg
	elif opt in ("-t", "--tfile"):
		tracefile = arg
	elif opt in ("-o", "--ofile"):
		outputfile = arg
	elif opt in ("-a"):
		r_w = arg
	elif opt in ("-e"):
		exefile = arg
	elif opt in ("-d"):
		d_i = arg


pinatrace = open(pinfile, "r")

pc_value_pm_accesses = []

pc_value_pm_accesses = pinatrace.readlines()
pinatrace.close()

del pc_value_pm_accesses[-1]
del pc_value_pm_accesses[0:3]

total = 0
pin_pc = {}       # address -> {pc}
pin_occ = {}      # address -> {occurence}
pin_addr = {}
pin_addr = set()
filtered_accesses = [] 

for lines in pc_value_pm_accesses:
	lines = lines.split(' ')
	try:
		del lines[5]
	except IndexError:
		pass 
	del lines[3:5]
	#del lines[1]
	addr = int(lines[2],0)
	pc = int(lines[0][:-1],0)
	if (r_w == lines[1]) :
		filtered_accesses.append(addr)
		pin_pc[addr] = pc 
		pin_addr.add(addr) 
		pin_occ[addr] = 0
	elif (r_w == '') : 
		filtered_accesses.append(addr)
		pin_addr.add(addr) 
		pin_pc[addr] = pc 
		pin_occ[addr] = 0


for addr in filtered_accesses:
	pin_occ[addr] += 1


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

if (d_i == 0):
	pin_addr = pin_addr.difference(trace_addr)
else :
	pin_addr = pin_addr.intersection(trace_addr)


pin_pc_dict = {}
for addr in pin_addr:
	pin_pc_dict[pin_pc[addr]] = 0

for addr in pin_addr:
	pin_pc_dict[pin_pc[addr]] += pin_occ[addr]
	
pin_occ_list = []
pin_pc_list = []

for pc in pin_pc_dict:
	pin_pc_list.append(pc)
	pin_occ_list.append(pin_pc_dict[pc])

pin_occ_list, pin_pc_list = zip(*sorted(zip(pin_occ_list, pin_pc_list), reverse=True))


pc_file = open(outputfile, "w")
pc_file.write("PC Value     :  Number of Accesses\n")
total = 0
for pc in pin_pc_list:
	pc_file.write("0x%0x : %d  : %s\n" %(pc, pin_pc_dict[pc], r_w))
	total += pin_pc_dict[pc]	 

pc_file.write("Total number of accesses : %d" %total)
pc_file.close()

bin_path = raw_input('Enter full path of benchmark file: ')

exefile = open(exefile, "w")
for pc in pin_pc_list:
	exefile.write("addr2line -e %s 0x%0x;\n" %(bin_path, pc))
exefile.close()

