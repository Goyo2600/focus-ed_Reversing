import os
from enum import Enum
#from pylfsr import LFSR

from prepare_code import sintetize_code

class action(Enum):
    ABRIR    = 0
    MALETERO = 1
    CERRAR   = 2

verbose     = 1
pipe_path   = "/tmp/codes"
lastcode    = 0x5587745fe5eeb6ce25f5
ofuscatedid = (lastcode & 0x00FFFFFFFF0000000000) >> 40 # ofuscated id
counter1    = 0xda                                      # first start byte in sequence
xorvalue    = 0x6c                                      
lfsr1       = counter1 ^ xorvalue
lfsr2       = 0x25                                      # counter
last_action = action.ABRIR

#highbyte    = (lfsr1 & 0xf0) >> 4
lowbyte     = 0
matrix = [[ 0, 2, -1], 
          [-2, 0, -3],
          [ 1, 3, 0]]



def getaction(action):
    if(action == action.ABRIR):
        return 0x20
    if(action == action.CERRAR):
        return 0x10
    if(action == action.MALETERO):
        return 0x40

def deofuscate(ofuscatedidkey):
    global lastcode
    direction=getdirection()
    if(direction):
        xorbyte = (lastcode & 0x000000000000FF000000) >> 32
    else:
        xorbyte = (lastcode & 0x00000000000000FF000000) >> 24

    return  ofuscatedidkey ^ (xorbyte << 8*3 | xorbyte << 8*2 | xorbyte << 8*1 | xorbyte)
    
def newofuscatedid(lfsr3):

    # mejor hacer newofuscatedid(lfsr3): 
    # return id_key ^ ( lfsr3 << 24 | lfsr3 << 16 | lfsr3 << 8 | lfsr3 )
    
    one   = lfsr3 ^ 0x49
    two   = one   ^ 0xf3
    three = two   ^ 0x2b
    four  = three ^ 0xba

    return one << 24 | two << 16 | three << 8 | four

def rotate_left(x, n):
    return int(f"{x:016b}"[n:] + f"{x:016b}"[:n], 2)

def rotate_right(val, r_bits, max_bits): 
    return ((val & (2**max_bits-1)) >> r_bits%max_bits) | (val << (max_bits-(r_bits%max_bits)) & (2**max_bits-1))

def getdirection():
    global lowbyte,xorvalue,lfsr2

    a = rotate_right(0x59a6,(xorvalue & 0x0f),16)
    lowbyte = ( lowbyte + 1 ) & 0x0f
    direction = a >> lowbyte & 1   

    if bin((lfsr2 & 0xf0) >> 4).count("1") % 2 == 0:
        direction = not direction

    return direction

def lfsr_back(action):
    global counter1,lowbyte,highbyte,xorvalue,lfsr1,lfsr2,last_action
    
    if(((counter1-1) & 0xf)  == 0x0f):
        counter1    = (counter1 -1) & 0x0f
        if(counter1    == 0xf):
            xorvalue = (xorvalue - 0x01) & 0x0f
            lfsr2 -= 0x01 & 0x0ff


    lfsr1       =  (((lowbyte-1) & 0xf) ^ xorvalue) | counter1 << 4
    lfsr2       += matrix[last_action.value][action.value] << 4 
    lfsr2       = (lfsr2 - 0x01) & 0x00ff


    lowbyte     = (lowbyte  - 1) & 0x0f
    last_action = action



def lfsr_next(new_action):
    global counter1,xorvalue,lfsr1,lfsr2,last_action
   
    if(counter1 + 1) == 0x100:
        counter1     = 0
        xorvalue     = (xorvalue + 1) & 0xff
        lfsr2        = (lfsr2 + 1) & 0xff
    else:
        counter1 = (counter1 + 1) & 0xff


    lfsr1       =  counter1 ^ xorvalue 
    lfsr2       += matrix[last_action.value][new_action.value] << 4 
    lfsr2       =  (lfsr2 + 0x01) & 0xff
    last_action = new_action

    
def getbackrollingcode(lastaction):
    global xorvalue,lfsr1,lfsr2,last_action
    
    lfsr_back(lastaction)
    direction=getdirection()

    #h =(lfsr1 & 0xf0) >> 4
    #l = lfsr1 & 0x0f
    
    if(direction): # I
        lfsr3 = (lfsr1 & 0xaa) ^ xorvalue
        rollingcode = (lfsr3 ^ getaction(lastaction))<<24  | (lfsr1 << 16) | (lfsr3 << 8) | lfsr2
    else:   #D
        lfsr3 = (lfsr1 & 0x55) ^ xorvalue
        rollingcode = (lfsr3 ^ getaction(lastaction))<<24  | (lfsr3 << 16) | (lfsr1 << 8) | lfsr2


    code = "55%08X%08X" % ( newofuscatedid(lfsr3),rollingcode ) 
    if(verbose):
        print("%s %s" % ( code, 'I' if direction else 'D'))
    
    return code
        

def getrollingcode(newaction,):
    global xorvalue,lfsr1,lfsr2,last_action
    
    lfsr_next(newaction)
    direction=getdirection()

    #h =(lfsr1 & 0xf0) >> 4
    #l = lfsr1 & 0x0f
    
    if(direction): # I
        lfsr3 = (lfsr1 & 0xaa) ^ xorvalue
        rollingcode = (lfsr3 ^ getaction(newaction))<<24  | (lfsr1 << 16) | (lfsr3 << 8) | lfsr2
    else:   #D
        lfsr3 = (lfsr1 & 0x55) ^ xorvalue
        rollingcode = (lfsr3 ^ getaction(newaction))<<24  | (lfsr3 << 16) | (lfsr1 << 8) | lfsr2


    code = "55%08X%08X" % ( newofuscatedid(lfsr3),rollingcode ) 
    if(verbose):
        print("%s %s" % ( code, 'I' if direction else 'D'))
    
    return code

def printStatus():
    print("Last code : %x" % (lastcode))
    print("Last lfsr : %02x%02x " % (lfsr1,lfsr2) )
    print("xor value : %02x  " % xorvalue)
    print("Direction : %s" % ( 'I' if getdirection() else 'D'))
#    print("ID key    : %08x" % deofuscate(ofuscatedid))

def emulate():
    i=0
    print("ABRIR")
    while i< 20:
        getrollingcode(action.ABRIR)
        i+=1

    i=0
    print("CERRAR")
    while i< 1:
        getrollingcode(action.CERRAR)
        i+=1
    i=0
    print("ABRIR")
    while i< 2:
        getrollingcode(action.CERRAR)
        i+=1



    i=0
    print("MALETERO")
    while i< 3:
        getrollingcode(action.MALETERO)
        i+=1
'''
    i=0
    print("ABRIR")
    while i< 25:
        getrollingcode(action.ABRIR)
        i+=1

    i=0    
    print("CERRAR")
    while i< 25:
        getrollingcode(action.CERRAR)
        i+=1
'''


# START #
try:
    os.remove(pipe_path) 
except:
    pass

try:
    os.mkfifo(pipe_path,0o777)
except:
    print("Failed to create FIFO: %s" % pipe_path)
    exit(1)
    

pipe_file = open(pipe_path, 'w')
printStatus()
while True:
    actioncode=action.ABRIR
    key=input("\nQué desea hacer?\ne EMULAR y SALIR\na ABRIR\nc CERRAR\nm MALETERO\nt ENVIAR CÓDIGO\nr RETROCEDER 15\nx RETROCEDER 100\nq SALIR\n>> ")
    key=key.upper()
    if(key == 'Q'):
        pipe_file.close()
        os.remove(pipe_path) 
        exit(0)

    if(key == "A"):
        actioncode=action.ABRIR
        code = getrollingcode(actioncode)

    elif(key == "C"):
        actioncode=action.CERRAR
        code = getrollingcode(actioncode)

    elif(key == "M"):
        actioncode=action.MALETERO
        code =  getrollingcode(actioncode)

    elif(key == "T"):
        code = input("Introduce codigo empezando por 55 : ")

    elif(key == "E"):
        emulate()
        exit(0)

    elif(key == "R"):
        actioncode=last_action
        verbose = 0
        i=0
        print("RETROCEDIENDO 15")
        while i< 14:
            getbackrollingcode(actioncode)
            i+=1
        verbose = 1 
        code = getbackrollingcode(actioncode)

    elif(key == "X"):
        actioncode=last_action
        verbose = 0
        i=0
        print("RETROCEDIENDO 100")
        while i< 100:
            code = getbackrollingcode(actioncode)
            i+=1
        verbose = 1 
        


    sintetize_code(pipe_file,code)



