########################################################################################
# Soviet microcomputer partial emulation
#
# DISCLAMER. This is not a MK85C clone! Coincidences are accidental.
# Version 0.1.
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


#===========================================================================================
# Charset (tweaked KOI-8, 96 characters)

charset = ' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[Ъ]…ЁЮАБЦДЕФГХИЙКЛМНОПЯРСТУЖВЬЫЗШЭЩЧ█    '

#===========================================================================================



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

    out_data = bytearray(data)

    R0 = (table_1[elementary_round.internal_state] + key[offset]) % 100 # Range 0 to 99.
    R2 = data[offset % BLOCK_SIZE]
    elementary_round.internal_state = (100 + elementary_round.internal_state + R0 - R2) % 100 # Range 0 to 99.
    out_data[offset % BLOCK_SIZE] = R0
        
    return bytes(out_data)
    

def full_round(data, key):

    out_data = bytearray(data)

    for i in range(KEY_LENGTH):
        out_data = elementary_round(out_data, key, i)

    return bytes(out_data)
    
    
# Get blocks_n pieces of stream, BLOCK_SIZE each.
def stream(mrk, key, blocks_n):

    mrk *= 2
    mrk_ext = bytearray(BLOCK_SIZE)
    initial_state = 0

    for i in range(BLOCK_SIZE):
        mrk_ext[i] = (mrk[i] // 16 * 10) + mrk[i] % 16
        initial_state = (initial_state + mrk_ext[i]) % 100

    buffer = bytes(mrk_ext)
    elementary_round.internal_state = initial_state

    temp = b''
    
    for ii in range(6):
        buffer = full_round(buffer, key)
        #print(buffer.hex())
        temp = temp + buffer
        
    #print(temp.hex())

    new_key = bytearray(KEY_LENGTH)
    for i in range(KEY_LENGTH):
        new_key[i] = (key[i] + temp[i]) % 100 # Range 0 to 99.
        
    new_key = bytes(new_key)
    #print(new_key.hex())

    temp = b''
    
    for ii in range(blocks_n):
        buffer = full_round(buffer, new_key) 
        temp = temp + buffer

    #print(temp.hex())
    
    return temp


#===========================================================================================


#===========================================================================================
# CS calc

def cs(key):

    # @371E: 4A380E2109 4A380E2109 hex is 7456143309 dec, a magic number...
    mrk = bytes.fromhex('7456143309')
    cs_raw = stream(mrk, key, 1)    
    
    # @3764
    cs_mask = bytes.fromhex('01000705030209080406')

    cs = bytearray(10)
    for i in range(5):
        temp = cs_raw[i] // 10 - cs_mask[i * 2]
        if(temp < 0):
            temp += 10
        cs[i * 2] = temp
        temp = cs_raw[i] % 10 - cs_mask[i * 2 + 1]
        if(temp < 0):
            temp += 10
        cs[i * 2 + 1] = temp
        #print(cs_raw[i:i + 1].hex())
        
    print(cs.hex())

    return bytes(cs)


#===========================================================================================







#===========================================================================================
# Raw key to printable

def key_to_str(key):

    out_string = ''

    for i in range(50):
        out_string += f'{key[i]:>02}'
        
    for i in range(50, 60):
        out_string += f'{key[i]:>01}'
        
    return ' '.join(textwrap.wrap(out_string, 5))
    
    
# Ctext string to (mrk, raw_ctext)

def str_to_mrk_ctext(string):

    temp = string.replace(' ', '')

    if(len(temp) % 2):
        temp += '0'
        
    temp = bytes.fromhex(temp)

    mrk = temp[0:5]
    ctext = bytearray(temp[5:])
    
    for i in range(len(ctext)):
        ctext[i] = (ctext[i] // 16 * 10) + ctext[i] % 16
    
    ctext = bytes(ctext)
        
    return mrk, ctext


#===========================================================================================



#===========================================================================================
# Higher level functions


def decrypt_letters(ctext, key):

    mrk, ctext = str_to_mrk_ctext(ctext)

    s = stream(mrk, key, math.ceil(len(ctext) / 10))
    #print(s.hex())

    ptext = ''
    output_raw = bytearray(len(ctext))

    for i in range(len(ctext)): # Do it digitwise (decimal)! A single character is equal to TWO digits!
        output_raw[i] = (10 + s[i] // 10 - ctext[i] // 10) % 10 * 10
        output_raw[i] += (10 + s[i] % 10 - ctext[i] % 10) % 10
        ptext += charset[output_raw[i]]

    #print(output_raw.hex())
    return ptext
    

#===========================================================================================


