# recibe un código 0x55... le añade las cabeceras, y repite el código 7 veces.
# la cod/decodificación manchester se hace de byte a byte

import sys
#from pynput  import keyboard
from inputimeout import inputimeout, TimeoutOccurred
#from manchester_code import encode, decode, decode_bits
'''
1space>[362]
<0space[2021]>0101010101
<0space[ 176]>01010101011101101000010110101110000101000001111100111111111111001110000101000010 : 0x557685ae141f3ffce142
<0space[2587]>0101010101
<0space[ 176]>01010101011101101000010110101110000101000001111100111111111111001110000101000010 : 0x557685ae141f3ffce142
<0space[2587]>0101010101
<0space[ 176]>01010101011101101000010110101110000101000001111100111111111111001110000101000010 : 0x557685ae141f3ffce142
<0space[2587]>0101010101
<0space[ 177]>01010101011101101000010110101110000101000001111100111111111111001110000101000010 : 0x557685ae141f3ffce142
<0space[2587]>0101010101
<0space[ 177]>01010101011101101000010110101110000101000001111100111111111111001110000101000010 : 0x557685ae141f3ffce142

'''
cte_rep_s= 13
cte_rep_l= 26
_1space  = 362
_0space  = 2021
zero     = "\x00"
uno      = "\x01"
preamble = uno * cte_rep_s + (zero * cte_rep_l + uno * cte_rep_l) * 4 + zero * cte_rep_l + uno * cte_rep_s  # 0b0101010101
short_0s = 175
long_0s  = 2573
last_byte= [0x00,0x03,0x05,0x06,0x09,0x0A,0x0C,0x0F,
            0x11,0x12,0x14,0x17,0x18,0x1B,0x1D,0x1E,
            0x21,0x22,0x24,0x27,0x28,0x2B,0x2D,0x2E,
            0x30,0x33,0x35,0x36,0x39,0x3A,0x3C,0x3F,
            0x41,0x42,0x44,0x47,0x48,0x4B,0x4D,0x4E,
            0x50,0x53,0x55,0x56,0x59,0x5A,0x5C,0x5F,
            0x60,0x63,0x65,0x66,0x69,0x6A,0x6C,0x6F,
            0x71,0x72,0x74,0x77,0x78,0x7B,0x7D,0x7E,
            0x81,0x82,0x84,0x87,0x88,0x8B,0x8D,0x8E,
            0x90,0x93,0x95,0x96,0x99,0x9A,0x9C,0x9F,
            0xA0,0xA3,0xA5,0xA6,0xA9,0xAA,0xAC,0xAF,
            0xB1,0xB2,0xB4,0xB7,0xB8,0xBB,0xBD,0xBE,
            0xC0,0xC3,0xC5,0xC6,0xC9,0xCA,0xCC,0xCF,
            0xD1,0xD2,0xD4,0xD7,0xD8,0xDB,0xDD,0xDE,
            0xE1,0xE2,0xE4,0xE7,0xE8,0xEB,0xED,0xEE,
            0xF0,0xF3,0xF5,0xF6,0xF9,0xFA,0xFC,0xFF]

def setup_code(code):
    result  = zero * _0space
    result += uno  * _1space
    result += zero * _0space

    mc = ""
    for i in range(0,20,2):
        v = int(code[i:i+2],16)
        for n in range(8):
            b =  v & (0x80 >> n)
            if b == 0:
                mc += uno * cte_rep_s + zero * cte_rep_s
            else:
                mc += zero * cte_rep_s + uno * cte_rep_s

    for n in range(7):
        result += preamble
        result += zero * short_0s
        result += mc
        result += zero * long_0s


    return result



def encode_manchester(bindata):
    manchester_code = encode([bindata])
    return manchester_code
def manchester2string(bindata):
    manchester_code_string = ''.join(['{:08b}'.format(m) for m in bindata])
    return manchester_code_string

def sintetize_code(f,code):
    final_code  = ''
    code_str    = code

    index       = 0
    if len(code_str) == 18: # 556695be040f2fc4f9--      
        for index in range(128):
            try:
                code_n      = "%s%02X" % (code_str,last_byte[index])
                prompt      = "%s" % (code_n)
                inputimeout(prompt,timeout=0.1)
                return
            except TimeoutOccurred:
                final_code  = setup_code(code_n)
                f.write(final_code)
                f.flush()
            

    elif len(code_str) == 20: # 556695be040f2fc4f948
        final_code = setup_code(code_str)
        f.write(final_code)
        f.flush()

    else:
        print("Error: size code must be 22 chars starting with 0x")
        exit(1)




