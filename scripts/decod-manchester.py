import sys

#filename="./focus2010/llave5-binary"
#filename="./prepare_code.bin"

msb         =True
ieee802     =True
idx         = 0
uno         = 0
cero        = 0
clock       = 0
code        = ""
flancodown  = 0
last        = 0
minlevel    = range(10,17)
maxlevel    = range(23,30)
space       = 30

if(len(sys.argv) > 1):
    if(sys.argv[1] == 'lsb'):
        msb=False
    if(sys.argv[1] == 'msb'):
        msb=True
    if(sys.argv[2] == 'ieee802'):
        ieee802=True
    if(sys.argv[2] == 'thomas'):
        ieee802=False
else:
    print("Options for: " + sys.argv[0] + " lsb|msb ieee802|thomas file")
    exit(-1)

filename=sys.argv[3]
with open(filename, "rb") as binary_file:
    # Read the whole file at once
    data = binary_file.read()

while(idx < len(data)):
    if data[idx] == 0:
        cero += 1
        if(last == 1):
            flancodown = 1
        last =  0
    else:
        if data[idx] == 1:
            uno  += 1
            last  = 1
            flancodown = 0


    #print("["+str(cero) + ":" +str(uno)+"]",end='') 
    if flancodown == 1:
        if cero > space and uno in minlevel:
            code += "<0space[%4d]>1" % cero
        if cero > space and uno in maxlevel:
            code += "<0space>11"
        if cero in minlevel  and uno in minlevel:
            code += "01" 
        if cero in maxlevel and uno in minlevel:
            code += "001"
        if cero in minlevel  and uno in maxlevel:
            code += "011"
        if cero in maxlevel and uno in maxlevel:
            code += "0011"

        if(cero > space and uno > space):
            code += "<0space>[%d]<1space>[%d]" % (cero,uno)

        flancodown  = 0
        uno         = 0
        cero        = 1



    idx   += 1

#print(code+"\n\n\n\n")
#exit(1)
idx=0
codedef=""
while(idx < len(code)-1):

    if code[idx] == '[':
        while(code[idx] != ']'):
            codedef += code[idx]
            idx += 1
        continue
    
    #print(code[idx]+code[idx+1])
    if(code[idx] == '0' and code[idx+1]) == '1':
        if(not ieee802):
            codedef += '0'
        else:
            codedef += '1'
        idx+=2
        continue
    if(code[idx] == '1' and code[idx+1]) == '0':
        if(not ieee802):
            codedef += '1'
        else:
            codedef += '0'
        idx+=2
        continue
    if(code[idx] == '1' and code[idx+1] == '<'):
        if(not ieee802):
            codedef += '1'
        else:
            codedef += '0'
        idx+=1
        continue

    if((code[idx] == '1' and code[idx+1] == '1') or (code[idx] == '0' and code[idx+1] == '0')):
        print("Error")
        print(code[0:idx+2])
        break
    else:
        codedef += code[idx] + code[idx+1]
        idx+=2





codedef += code[idx-1]+"<0space>"
codedef = codedef.replace("<","\n<")
if(not msb):
    print("LSB MODE")
    print("TODO")
else:
    print("MSB MODE")
    #print(codedef)
    lines = codedef.split('\n')
    #print(lines)
    for line in lines:
        #print(line)
        if(len(line) > 30):
            print(line,end=' : ')
            print(hex(int(line[14:], 2)))
        else:
            print(line)


