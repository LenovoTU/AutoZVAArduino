""""
Find the instruments in your environment
"""
from RsInstrument import *
# Use the instr_list string items as resource names in the RsInstrument constructor
instr_list = RsInstrument.list_resources("?*")
print(instr_list)

case_1 = 'ASRL1::INSTR'
case_2 = 'TCPIP::192.168.210.178::INSTR'
instr = RsInstrument(case_2)

idn = instr.query_str('*IDN?')
print(f'\n Hello, i am  {idn}')