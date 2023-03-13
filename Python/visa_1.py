from RsInstrument import *
import matplotlib.pyplot as plt
from time import time

rtm = None
try:
	rtm = RsInstrument('TCPIP::192.168.210.178::INSTR', True, False)
	rtm.visa_timeout = 15000  # Timeout for VISA Read Operations
	rtm.opc_timeout = 15000  # Timeout for opc-synchronised operations

	rtm.instrument_status_checking = True  # Error check after each command
except Exception as ex:
	print('Error initializing the instrument session:\n' + ex.args[0])
	exit()

print(f'RTM3002 IDN: {rtm.idn_string}')
print(f'RTM3002 Options: {",".join(rtm.instrument_options)}')
rtm.clear_status()
rtm.reset()
# -----------------------------------------------------------
# Basic Settings:
# ---------------------------- -------------------------------
print("Try to Load basic Setting's")
rtm.write_str("ACQ:POIN:AUT ON")  # Define Horizontal scale by number of points
# rtm.write_str("TIM:RANG 0.01")  # 10ms Acquisition time
# rtm.write_str("ACQ:POIN 20002")  # 20002 X points
# rtm.write_str("CHAN1:RANG 2")  # Horizontal range 2V
# rtm.write_str("CHAN1:POS 0")  # Offset 0
rtm.write_str("CHAN1:STAT ON")  # Switch Channel 1 ON
# -----------------------------------------------------------
# Trigger Settings:
# -----------------------------------------------------------
print("Try to Load Trigger Setting's")
rtm.write_str("TRIG:A:MODE AUTO")  # Trigger Auto mode in case of no signal is applied
rtm.write_str("TRIG:A:SOUR CH1")  # Trigger source CH1
rtm.query_opc()  # Using *OPC? query waits until all the instrument settings are finished
# -----------------------------------------------------------
# SyncPoint 'SettingsApplied' - all the settings were applied
# -----------------------------------------------------------
# -----------------------------------------------------------
rtm.VisaTimeout = 100000  # Acquisition timeout - set it higher than the acquisition time
# -----------------------------------------------------------
# DUT_Generate_Signal() - in our case we use Probe compensation signal
# where the trigger event (positive edge) is reoccurring
# -----------------------------------------------------------
rtm.write_str("AUT") # Autoscale
# -----------------------------------------------------------
rtm.query_opc()  # Using *OPC? query waits until the instrument finished the Acquisition
# -----------------------------------------------------------
# SyncPoint 'AcquisitionFinished' - the results are ready
# -----------------------------------------------------------
# Fetching the waveform in ASCII and BINary format
# -----------------------------------------------------------
print("Try to get data from RTM")
dest = "/USB_FRONT/WF"
rtm.write_str("FORMAT CSV")
for i in range(5):
    rtm.write_str("EXPort:WAVeform:SOURce CH1")
    rtm.write_str(fr"EXPort:WAVeform:NAME '/USB_FRONT/Wf{i}'")
    rtm.query_opc()
    rtm.write_str("EXPort:WAVeform:SAVE")
# t = time()
# trace = rtm.query_bin_or_ascii_float_list('FORM ASC;:CHAN1:DATA?')  # Query ascii array of floats
# print(f'Instrument returned {len(trace)} points in the ascii trace, query duration {time() - t:.3f} secs')
# t = time()
# rtm.bin_float_numbers_format = BinFloatFormat.Single_4bytes  # This tells the driver in which format to expect the binary float data
# trace = rtm.query_bin_or_ascii_float_list('FORM REAL,32;:CHAN1:DATA?')  # Query binary array of floats - the query function is the same as for the ASCII format
# print(f'Instrument returned {len(trace)} points in the binary trace, query duration {time() - t:.3f} secs')

# # -----------------------------------------------------------
# # Making an instrument screenshot and transferring the file to the PC
# # -----------------------------------------------------------
# rtm.write_str('HCOP:DEV:LANG PNG')  # Set the screenshot format
# rtm.write_str(r"MMEM:NAME 'c:\temp\Dev_Screenshot.png'")  # Set the screenshot path
# rtm.write_str("HCOP:IMM")  # Make the screenshot now
# rtm.query_opc()  # Wait for the screenshot to be saved
# rtm.read_file_from_instrument_to_pc(r'c:\temp\Dev_Screenshot.png', r'c:\Temp\PC_Screenshot.png')  # Query the instrument file to the PC
# print(r"Screenshot file saved to PC 'c:\Temp\PC_Screenshot.png'")

# Close the session
rtm.close()

# data = instr.query_binary_values('WAV:DATA?', 'h', is_big_endian=True)  # acquire waveform data
# x_incr = float(instr.query('WAV:XINC?'))  # get the x-axis increment
# x_zero = float(instr.query('WAV:XOR?'))  # get the x-axis zero point
# y_incr = float(instr.query('WAV:YINC?'))  # get the y-axis increment
# y_zero = float(instr.query('WAV:YREF?'))  # get the y-axis reference level

# # Plot the waveform data
# x = [(i * x_incr) + x_zero for i in range(len(data))]  # compute the x-axis values
# y = [(i * y_incr) + y_zero for i in data]  # compute the y-axis values
# plt.plot(x, y)
# plt.xlabel('Time (s)')
# plt.ylabel('Voltage (V)')
# plt.show()

# Disconnect from the oscilloscope
