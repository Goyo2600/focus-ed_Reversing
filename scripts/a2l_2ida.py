import csv
import idc
import idaapi

# Convert range to code (e.g. processrom(0x10000, 0x20000))
def processrom(min, max):
	if min > 0:
		min = min - 1
	curaddr = idc.FindUnexplored(min, idc.SEARCH_DOWN)
	while curaddr < max:
		if idc.MakeFunction(curaddr) != True:
			idc.MakeCode(curaddr)
		curaddr = idc.FindUnexplored(curaddr, idc.SEARCH_DOWN)

	return

 
# opening the CSV file
def csv2ida(filename):
    with open(filename, mode ='r') as file:
   
        # reading the CSV file
        csvFile = csv.reader(file)
 
        # displaying the contents of the CSV file
        for lines in csvFile:
            addr        = int(lines[0],0)
            name        = lines[1]
            id          = lines[2]
            idc.MakeWord(addr);
            idc.MakeNameEx(addr, id, 1)
            idc.MakeRptCmt(addr,name);



# Load a2l (e.g. a2l("C:\my.a2l")):
def a2l(filename):
	lastvarname = ""
	lastaddress = ""
	with open(filename) as fp:
		measurements = fp.read().split("/begin MEASUREMENT")
		measurements.pop(0)
		print("Found: %d measurement(s)" % len(measurements))
		for m in measurements:
			namefound = 0
			addrfound = 0
			name = ""
			addr = ""
			for l in m.split("\n"):
				l = l.strip()
				if (len(l) > 0):
					if (namefound == 0):
						name = l
						namefound = 1
					elif (l.startswith("ECU_ADDRESS")):
						addr = l[12:]
						addrfound = 1
						break
			if (addrfound != 1):
				print("ERROR")
			else:
                                print("Measurement makename: %s at %x" % (name,int(addr,0)))
				idc.MakeNameEx(int(addr, 0), name, 1)
    
        fp.close()
	return

#Parse tricore indirect registers. Will replace ram+offset with actual value, so it can be crossreferenced and maps to a2l (e.g. indirect("a0", 0xDA80)):
def indirect(register, address):
	print("Loading assembly...")
	counter = 0
	heads = list(idautils.Heads())
	total = len(heads)
	last = 0
	replaced = 0
	print("Parsing assembly...")
	for line in idautils.Heads():
		if (idc.Byte(line) == 0xD9 or idc.Byte(line) == 0x19 or idc.Byte(line) == 0x59 or idc.Byte(line) == 0x99):
			dis = idc.GetDisasm(line)
			pos = dis.find("[" + register + "]0x")
			if (pos == -1):
				pos = dis.find("[" + register + "]-0x")
			if pos != -1:
				replaced += 1
				idc.OpOffEx(line, 1, idc.REF_OFF32, -1, address, 0x0)
		cur = math.floor(counter*100/total)
		if (cur >= (last+10)):
			print("%d" % cur, end="%...")
			last = cur
		counter += 1

	print("100%")
	print("All done, %d entries replaced." % replaced)
	return

