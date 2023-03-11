from PyQt5 import QtWidgets, QtCore
import zva_ui as gui
# from list_local_network import get_devices_on_network
from RsInstrument import *
from time import *
import serial
from serial_list import serial_ports
import json


## TO - DO
## Split on Thread all code
##


class MeasurmentsThread(QtCore.QThread):
    signalSendData = QtCore.pyqtSignal(str)

    def __init__(self, device):
        QtCore.QThread.__init__(self)
        self.Device = device
        self.terminate = False

    def run(self):
        print("Arduino")
        while not self.terminate:
            # Endless cycle
            data = self.Device.readline().decode('utf-8').rstrip()
            if data != None:
                # Check if the received data can be converted to a float
                try:
                    self.current_temperature = float(data)
                    self.signalSendData.emit(data)
                except ValueError:
                    pass

    def stop(self):
        self.terminate()


# For ZVA - 40
# Testing push
class InstrumentThread(QtCore.QThread):
    signalSaveData2 = QtCore.pyqtSignal(str)

    def __init__(self, instrument, device, measurment_time):
        QtCore.QThread.__init__(self)
        self.Instrument = instrument
        self.MeasTime = measurment_time
        self.Device = device
        self.thread1 = MeasurmentsThread(device=self.Device)
        self.thread1.signalSendData.connect(self.handle_data, QtCore.Qt.QueuedConnection)
        self.terminate = False

    def run(self):
        self.thread1.start()

    def handle_data(self, data):
        print(f"Data:{data}")
        # --------------------------
        self.Instrument.write_str_with_opc('CALCulate1:PARameter:MEAsure "Trc1", "S11"')
        self.Instrument.write_str_with_opc('CALCulate1:PARameter:MEAsure "Trc2", "S21"')
        self.Instrument.write_str_with_opc('CALCulate1:PARameter:MEAsure "Trc3", "S12"')
        self.Instrument.write_str_with_opc('CALCulate1:PARameter:MEAsure "Trc4", "S22"')

        self.Instrument.write_str_with_opc('CALCulate1:PARameter:SDEFine "Trc1", "S11"')  # Add a second trace
        self.Instrument.write_str_with_opc('CALCulate1:PARameter:SDEFine "Trc2", "S21"')
        self.Instrument.write_str_with_opc('CALCulate1:PARameter:SDEFine "Trc3", "S12"')
        self.Instrument.write_str_with_opc('CALCulate1:PARameter:SDEFine "Trc4", "S22"')

        self.Instrument.write_str_with_opc('SYSTEM:DISPLAY:UPDATE ON')
        self.Instrument.write_str_with_opc('CALCulate1:Format MLOGarithmic')  # Change active trace's format to phase
        self.Instrument.write_str_with_opc(':INITiate1:CONTinuous ON')
        self.Instrument.write_str_with_opc(':DISPlay:WINDOW:STATE ON')
        if data != None:
            print("Instrument")
            self.Instrument.write_str_with_opc(':INITiate1:CONTinuous OFF')
            self.Instrument.write_str_with_opc(':INITiate:IMMediate')
            self.Instrument.write_str_with_opc(':DISPlay:WINDow:TRACe1:FEED "Trc1"')
            self.Instrument.write_str_with_opc(':DISPlay:WINDow:TRACe2:FEED "Trc2"')
            self.Instrument.write_str_with_opc(':DISPlay:WINDow:TRACe3:FEED "Trc3"')
            self.Instrument.write_str_with_opc(':DISPlay:WINDow:TRACe4:FEED "Trc4"')
            # s2p_filename = fr'C:\Users\Public\Documents\Rohde-Schwarz\Vna\Traces\CTEM_{data}.s2p'  # Name and path of the s2p file on the instrument
            pc_filename = fr'D:\Vitalya\CTEM_{data}.s2p'  # Name and path of the s2p file on the PC
            # self.Instrument.write_str_with_opc(r':MMEMory:CDIRectory "C:\Rohde&Schwarz\Nwa\Traces"')
            self.Instrument.write_str_with_opc(fr":MMEM:STOR:TRAC:PORT 1,  'Test.s2p', COMPlex, 1, 2")
            self.Instrument.read_file_from_instrument_to_pc('Test.s2p', pc_filename)
            sleep(self.MeasTime)


# Oscill example
# class InstrumentThread(QtCore.QThread):
#     signalSaveData2 = QtCore.pyqtSignal(str)
#
#     def __init__(self, instrument, device, measurment_time):
#         QtCore.QThread.__init__(self)
#         self.Instrument = instrument
#         self.MeasTime = measurment_time
#         self.Device = device
#         self.thread1 = MeasurmentsThread(device=self.Device)
#         self.thread1.signalSendData.connect(self.handle_data, QtCore.Qt.QueuedConnection)
#         self.terminate = False
#
#     def run(self):
#         self.thread1.start()
#
#     def handle_data(self, data):
#         print(f"Data:{data}")
#         self.Instrument.write_str("ACQ:POIN:AUT ON")
#         self.Instrument.write_str("CHAN1:STAT ON")
#         self.Instrument.write_str("TRIG:A:MODE AUTO")
#         self.Instrument.query_opc()
#         self.Instrument.write_str("AUT")
#         while not self.terminate:
#             if data != None:
#                 print("Instrument")
#                 self.Instrument.write_str(r"EXP:WFMS:DEST '/USB_FRONT'")
#                 self.Instrument.write_str("FORMAT CSV")
#                 self.Instrument.write_str("EXPort:WAVeform:SOURce CH1")
#                 self.Instrument.write_str(fr"EXPort:WAVeform:NAME '/USB_FRONT/Wf{data}'")
#                 self.Instrument.query_opc()
#                 self.Instrument.write_str("EXPort:WAVeform:SAVE")
#                 self.signalSaveData2.emit(f"Save to /USB_FRONT/Wf{data}.csv")
#                 sleep(self.MeasTime)

class ExampleApp(QtWidgets.QMainWindow, gui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.Device = serial.Serial(None)
        self.measurements_time = {'minutes': 0,
                                  'seconds': 0,
                                  'total_seconds': 0}
        self.current_temperature = 0
        self.process = False
        self.setupUi(self)
        # Buttons
        self.pushButtonFindDevice.clicked.connect(self.findDevice)
        self.pushButtonConnect.clicked.connect(self.connect2Device)
        self.pushButtonSetup.clicked.connect(self.setup)
        self.pushButtonStart.clicked.connect(self.start)
        self.pushButtonStop.clicked.connect(self.stop)
        # Threading

    def findDevice(self):
        ip_list = ['192.168.2.108', '192.168.2.109']
        com_list = serial_ports()
        self.textBrowser.append(
            f'Total devices found in the local network: {len(ip_list)} and COM ports: {len(com_list)}')
        # ComboBox
        self.deviceBox.addItems(serial_ports())
        self.instrBox.addItems(ip_list)

    def connect2Device(self):
        self.pushButtonConnect.setDisabled(True)
        connected_device = r'192.168.2.108'
        connected_device = self.instrBox.currentText()
        self.textBrowser.append(f'Try to conncect to:{connected_device}')
        resource = f'TCPIP::{connected_device}::INSTR'
        self.Instrument = RsInstrument(resource)
        self.Instrument.visa_timeout = 15000  # Timeout for VISA Read Operations
        self.Instrument.opc_timeout = 15000  # Timeout for opc-synchronised operations
        self.Instrument.VisaTimeout = 100000
        self.Instrument.instrument_status_checking = True  # Error check after each command, can be True or False
        self.Instrument.clear_status()

        idn = self.Instrument.query_str('*IDN?')
        sleep(1)
        self.textBrowser.append(f'Connect to {idn}')

        port = self.deviceBox.currentText()
        self.Device = serial.Serial(f'{port}', baudrate=9600,
                                    bytesize=serial.EIGHTBITS,
                                    parity=serial.PARITY_NONE,
                                    stopbits=serial.STOPBITS_ONE,
                                    xonxoff=True,
                                    timeout=1)
        self.textBrowser.append(f'Connect to {port}')

    def setup(self):
        # Dict 
        self.measurements_time = {'minutes': 0, 'seconds': 0, 'total_seconds': 0}
        # Get the time values from the QTimeEdit widget
        temp = self.timeEdit.time()
        minutes = temp.minute()
        seconds = temp.second()
        # Store the time values in the dictionary
        self.measurements_time['minutes'] = minutes
        self.measurements_time['seconds'] = seconds
        self.measurements_time['total_seconds'] = minutes * 60 + seconds
        # Print the time values
        print(self.measurements_time)
        # Add the time values to the text browser
        formatted_time = f"{minutes:02d}:{seconds:02d}"
        self.textBrowser.append(f"Measurements time is set: {formatted_time}")
        # Send data do arduino        
        self.json_string = json.dumps(self.measurements_time)
        self.Device.write(self.json_string.encode())
        self.textBrowser.append(f'Sent measurements time to Arduino: {self.json_string}')

        self.measurements_thread = MeasurmentsThread(self.Device)
        self.instrument_thread = InstrumentThread(self.Instrument, self.Device, seconds)
        print(self.Device)
        # -----------------------------------------------------------
        # Create thread for Arduino
        # -----------------------------------------------------------
        # self.measurements_thread.started.connect(self.start)
        # self.measurements_thread.signalSendData.connect(self.change, QtCore.Qt.QueuedConnection)
        # 
        self.instrument_thread.started.connect(self.start)
        self.instrument_thread.signalSaveData2.connect(self.change2, QtCore.Qt.QueuedConnection)
        #
        # Create thead for R&S instruments
        #

    def start(self):
        print("Start")
        self.pushButtonStart.setDisabled(True)
        self.pushButtonStop.setDisabled(False)
        # self.measurements_thread.start()
        self.instrument_thread.start()

    def change(self, s):
        if s != None:
            print(f"Time:{self.json_string} Data:{s}")
            self.textBrowser.append(s)

    def change2(self, s):
        if s != None:
            print(f"Save data:{s}")
            self.textBrowser.append(s)

    def stop(self):
        self.pushButtonStart.setDisabled(False)
        self.pushButtonStop.setDisabled(True)
        print("Stop")
        # self.measurements_thread.quit()
        # self.measurements_thread.terminate = True

        self.instrument_thread.quit()
        self.instrument_thread.terminate = True


def main():
    app = QtWidgets.QApplication([])
    window = ExampleApp()
    window.show()
    app.exec()


main()
