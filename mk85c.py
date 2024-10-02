########################################################################################
# Soviet microcomputer partial emulation
#
# DISCLAMER. This is not a MK85C clone! Coincidences are accidental.
# Version 0.6.
# 2024  kaseiiro@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
########################################################################################


import textwrap
import math
import secrets


#===========================================================================================
# Charset (tweaked KOI-8, 96 characters)

charset = ' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[Ъ]…ЁЮАБЦДЕФГХИЙКЛМНОПЯРСТУЖВЬЫЗШЭЩЧ█    '


#===========================================================================================
# Ang*trom-3? USSR Ti*er?

KEY_LENGTH = 50
BLOCK_SIZE = 10


# @32E4 @347A
# LFSR?
table_1 = bytes.fromhex("060E284256 0852554D44 43021A1735 3361463039 \
                         3A25180B00 4A10515F34 212D2B5A57 3E3F114963 \
                         092623074E 32222E4803 010D130F3B 5941622C36 \
                         401F5B0C47 533C20604C 14501B045E 243D5D270A \
                         5C312A5837 2F124F1E29 05381C4516 191D54154B")


def elementary_round(data, key, offset):

    R0 = (table_1[elementary_round.internal_state] + key[offset]) % 100 # Range 0 to 99.
    R2 = data[offset % BLOCK_SIZE]
    elementary_round.internal_state = (100 + elementary_round.internal_state + R0 - R2) % 100 # Range 0 to 99.
    data[offset % BLOCK_SIZE] = R0
        
    return data
    

def full_round(data, key):

    for i in range(KEY_LENGTH):
        data = elementary_round(data, key, i)

    return data
    
    
# Get blocks_n pieces of stream, BLOCK_SIZE each.
def stream(mrk, key, blocks_n):

    buffer = mrk * 2
    elementary_round.internal_state = sum(buffer) % 100

    temp = bytearray()
    
    for ii in range(6):
        buffer = full_round(buffer, key)
        temp += buffer
        
    new_key = bytearray(KEY_LENGTH)
    for i in range(KEY_LENGTH):
        new_key[i] = (key[i] + temp[i]) % 100 # Range 0 to 99.
        
    temp = bytearray()
    
    for ii in range(blocks_n):
        buffer = full_round(buffer, new_key) 
        temp += buffer
    
    return temp


#===========================================================================================
# CS calc

def cs(key):

    # @371E: 4A380E2109 4A380E2109 hex is 7456143309 dec, a magic number...
    mrk = fromdec('7456143309')
    cs_raw = stream(mrk, key, 1)    
    
    # @3764
    cs_mask = bytes.fromhex('01000705030209080406')

    cs = bytearray(10)
    for i in range(5):
        cs[i * 2] = (10 + cs_raw[i] // 10 - cs_mask[i * 2]) % 10
        cs[i * 2 + 1] = (10 + cs_raw[i] % 10 - cs_mask[i * 2 + 1]) % 10
        #print(cs_raw[i:i + 1].hex())
        
    #print(cs.hex())

    return bytes(cs)



#===========================================================================================

# Raw key to printable
def key_to_str(key):

    if(len(key) == 50):
        key += cs(key)
        
    if(len(key) != 60):
        raise Exception(f'Wrong raw key lenght! Got {len(key)}, must be 50 or 60.')

    out_string = ''

    for i in range(50):
        out_string += f'{key[i]:>02}'
        
    for i in range(50, 60):
        out_string += f'{key[i]:>01}'
        
    return ' '.join(textwrap.wrap(out_string, 5))
    
    
# Printable key to raw key
def str_to_key(string):

    temp = string.replace(' ', '')
    
    if(len(temp) != 110):
        raise Exception(f'Wrong key lenght! Got {len(temp)}, must be 110.')
    
    key = fromdec(temp[0:100])
    cs_in = fromdec_base10(temp[100:110])
    cs_calc = cs(key)
    #print(cs_in.hex(), cs_calc.hex())
    
    if(cs_in != cs_calc):
        print(f'Warning! Wrong key CS!')
    
    return key
    
    
# Raw mrk to printable
def mrk_to_str(mrk):

    if(len(mrk) != 5):
        raise Exception(f'Wrong raw mrk lenght! Got {len(mrk)}, must be 5.')

    out_string = ''

    for i in range(5):
        out_string += f'{mrk[i]:>02}'
        
    return out_string
    
    
# Ctext string to (mrk, raw_ctext)
def str_to_mrk_ctext(string, tweak = (0, 0)):

    temp = string.replace(' ', '')

    #=========== +/- 1 tweak ==================
    
    index = (tweak[0] - 1) * 2 + 10
    
    if(tweak[1] < 0):
        #temp = ('0' * (-tweak[1])).join([temp[:tweak[0] + 10], temp[tweak[0] + 10:]])
        temp = temp[:index] + '0' * (-tweak[1]) + temp[index:]
    if(tweak[1] > 0):
        temp = temp[:index] + temp[index + tweak[1]:]
    #==========================================
    

    if(len(temp) % 2):
        temp = temp[:-1] # For text mode only?
    
    mrk = fromdec(temp[0:10])
    ctext = fromdec(temp[10:])
    
    return mrk, ctext
    
    
# Similar to bytes.fromhex, but decimal; byte is 0 to 99
def fromdec(string):

    temp = bytearray.fromhex(string)
    
    for i in range(len(temp)):
        temp[i] = (temp[i] // 16 * 10) + temp[i] % 16
        
    return temp
    
    
# Similar to bytes.fromhex, but decimal; byte is 0 to 9
def fromdec_base10(string):

    temp = bytearray(len(string))
    
    for i in range(len(string)):
        temp[i] = int(string[i])
        
    return temp
    
    
# Raw dec to printable
def dec_to_str(data):

    out_string = ''

    for i in range(len(data)):
        out_string += f'{data[i]:>02}'

    return out_string


#===========================================================================================



#===========================================================================================
# Higher level functions


def decrypt_text(ctext, key, tweak = (0, 0)):

    mrk, ctext = str_to_mrk_ctext(ctext, tweak)
    
    k = str_to_key(key)

    s = stream(mrk, k, math.ceil(len(ctext) / BLOCK_SIZE))

    ptext = ''
    output_raw = bytearray(len(ctext))

    for i in range(len(ctext)): # Do it digitwise (decimal)! A single character is equal to TWO digits!
        output_raw[i] = (10 + s[i] // 10 - ctext[i] // 10) % 10 * 10
        output_raw[i] += (10 + s[i] % 10 - ctext[i] % 10) % 10
        ptext += charset[output_raw[i]]
        
    #=========== +/- 1 tweak ==================
    # Strip out damaged chars
    
    index = tweak[0] - 1
    
    if(tweak[1] < 0):
        ptext = ptext[:index] + ptext[index + math.ceil(-tweak[1] / 2):]
    #==========================================

    return ptext
    
    
def encrypt_text(ptext, key, group_n):

    full_ctext_len = math.ceil((10 + len(ptext) * 2) / group_n) * group_n
    ctext_len_wo_mrk = full_ctext_len - 10

    mrk = bytearray(5)
    for i in range(5):
       mrk[i] = secrets.randbelow(100)
    
    k = str_to_key(key)
    s = stream(mrk, k, math.ceil(ctext_len_wo_mrk / BLOCK_SIZE))
    ctext_raw_len = math.ceil(ctext_len_wo_mrk / 2)
    
    ctext = ''
    
    ptext_extended = ptext.upper() + ' ' * (ctext_raw_len - len(ptext))
    
    for i in range(ctext_raw_len):
        temp = charset.find(ptext_extended[i])
        if temp == -1:
            temp = 0

        ctext += f'{((10 + s[i] // 10 - temp // 10) % 10):>01}{((10 + s[i] % 10 - temp % 10) % 10):>01}' # Do it digitwise (decimal)! A single character is equal to TWO digits!

    return ' '.join(textwrap.wrap((mrk_to_str(mrk) + ctext)[0:full_ctext_len], group_n))
    

#===========================================================================================


