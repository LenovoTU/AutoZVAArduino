from PyQt5 import QtWidgets, QtCore
import zva_ui as gui
from list_local_network import get_devices_on_network
from RsInstrument import *
from time import *
import serial
from serial_list import serial_ports
import json


class MeasurmentsThread(QtCore.QThread):
    """
    A thread class that reads data from a device and emits a signal with the data.
    Attributes:
        signalSendData (QtCore.pyqtSignal): A signal that is emitted with the received data.
        Device: The device object that the thread reads data from.
        terminate (bool): A flag that indicates whether the thread should be terminated.
    Methods:
        run(): The method that is executed when the thread starts. It reads data from the device and emits the signal with the data.
        stop(): A method that sets the terminate flag to stop the thread.
    """
    data_sent = QtCore.pyqtSignal(str)
    def __init__(self, device):
        """
        Initializes a new instance of the MeasurmentsThread class.

        Args:
            device: The device object that the thread reads data from.
        """
        QtCore.QThread.__init__(self)
        self.Device = device
        self.terminate = False

    def run(self):
        """
        The method that is executed when the thread starts. It reads data from the device and emits the signal with the data.
        """
        while not self.terminate:
            data = self.Device.readline().decode('utf-8').rstrip()
            if data.strip():
                print(f"Data:{data}")
                # Convert the received data to a float and emit the signal with the data
                try:
                    self.current_temperature = data
                    print(f"DS18 temperature is:{self.current_temperature}")
                    self.data_sent.emit(self.current_temperature)
                # If the received data cannot be converted to a float, do nothing
                except ValueError:
                    pass
    def stop(self):
        """
        A method that sets the terminate flag to stop the thread.
        """
        self.terminate()

class InstrumentThread(QtCore.QThread):
    """
    This class represents the thread responsible for the measurement procedure.
    """
    data_saved = QtCore.pyqtSignal(str)
    def __init__(self, instrument, device, measurment_time):
        """
        Constructor for InstrumentThread class.
        Args:
            instrument: An instance of the instrument driver.
            device: An instance of the device driver.
            measurment_time: The time interval between measurements.
        """
        QtCore.QThread.__init__(self)
        self.Instrument = instrument
        self.MeasTime = measurment_time
        self.Device = device
        self.thread1 = MeasurmentsThread(device=self.Device)
        self.thread1.data_sent.connect(self.handle_data, QtCore.Qt.QueuedConnection)
        self.terminate = False
        self.counter = 0

    def run(self):
        """
        Starts the thread and runs the measurement procedure.
        """
        self.Instrument.write_str_with_opc(':INITiate1:CONTinuous ON')
        self.Instrument.write_str_with_opc(':DISPlay:WINDOW:STATE ON')
        self.Instrument.write_str_with_opc(':SYSTEM:DISPLAY:UPDATE ON')

        self.Instrument.write_str_with_opc('CALCulate1:PARameter:MEAsure "Trc1", "S11"')
        self.Instrument.write_str_with_opc('CALCulate1:PARameter:MEAsure "Trc2", "S21"')
        self.Instrument.write_str_with_opc('CALCulate1:PARameter:MEAsure "Trc3", "S12"')
        self.Instrument.write_str_with_opc('CALCulate1:PARameter:MEAsure "Trc4", "S22"')

        self.Instrument.write_str_with_opc('CALCulate1:PARameter:SDEFine "Trc1", "S11"')  # Add a second trace
        self.Instrument.write_str_with_opc('CALCulate1:PARameter:SDEFine "Trc2", "S21"')
        self.Instrument.write_str_with_opc('CALCulate1:PARameter:SDEFine "Trc3", "S12"')
        self.Instrument.write_str_with_opc('CALCulate1:PARameter:SDEFine "Trc4", "S22"')

        self.Instrument.write_str_with_opc('DISPlay:WINDow:TRACe1:FEED "Trc1"')
        self.Instrument.write_str_with_opc('DISPlay:WINDow:TRACe2:FEED "Trc2"')
        self.Instrument.write_str_with_opc('DISPlay:WINDow:TRACe3:FEED "Trc3"')
        self.Instrument.write_str_with_opc('DISPlay:WINDow:TRACe4:FEED "Trc4"')

        self.thread1.start()

    def handle_data(self, data):
        """
        A function that handles the received data from the device.
        Args:
            data: The received data from the device.
        """
        print(f"Temeperature form DS18:{data} C")
        # --------------------------
        if data != None:
            print(f"Measurment")

            self.Instrument.write_str_with_opc(':INITiate1:CONTinuous OFF')
            self.Instrument.write_str_with_opc(':INITiate:IMMediate')
            idn = self.Instrument.query_str('*IDN?')
            self.Instrument.write_str_with_opc(
                ':CALCulate1:Format MLOGarithmic')  # Change active trace's format to phase
            print(f"{idn}: Calcualte parameter(S-11 .. S-22) to Trace(1 .. 4)")
            print(f"{idn}: Create new trace and select name and measurments parameter")

            # s2p_filename = fr'C:\Users\Public\Documents\Rohde-Schwarz\Vna\Traces\CTEM_{data}.s2p'  # Name and path of the s2p file on the instrument
            # Менять название папки в которой сохраняются данные
            dir = r'sminus50do25'
            pc_filename = fr'D:\Vitalya\{dir}\CTEM_{data}_{self.counter}.s2p'  # Name and path of the s2p file on the PC
            #

            # self.Instrument.write_str_with_opc(r':MMEMory:CDIRectory "C:\Rohde&Schwarz\Nwa\Traces"')
            self.Instrument.write_str_with_opc(fr":MMEM:STOR:TRAC:PORT 1,  'Test.s2p', COMPlex, 1, 2")
            self.Instrument.read_file_from_instrument_to_pc('Test.s2p', pc_filename)
            print(f"Save data {pc_filename}")
            self.counter += 1
            self.Instrument.write_str_with_opc(':INITiate1:CONTinuous ON')
            sleep(self.MeasTime)

class ExampleApp(QtWidgets.QMainWindow, gui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.Device = serial.Serial(None)
        self.measurements_time = {'minutes': 0,
                                  'seconds': 0,
                                  'total_seconds': 0}
        # {'minutes': 0, 'seconds': 2, 'total_seconds': 0}
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
        """
        This function searches for available devices and displays them on the user interface.
        Returns:
            None
        """
        ip_list  = ['192.168.2.108', '192.168.2.109'] # Example for Lab
        # ip_list  = get_devices_on_network() 
        com_list = serial_ports()
        self.textBrowser.append(
            f'Total devices found in the local network: {len(ip_list)} and COM ports: {len(com_list)}')
        # ComboBox
        self.deviceBox.addItems(com_list)
        self.instrBox.addItems(ip_list)

    def connect2Device(self):
        self.pushButtonConnect.setDisabled(True)
        connected_device = r'192.168.2.108'
        connected_device = self.instrBox.currentText()
        self.textBrowser.append(f'Try to conncect to:{connected_device}')
        resource = f'TCPIP::{connected_device}::INSTR'
        self.Instrument = RsInstrument(resource)
        self.Instrument.visa_timeout = 5000  # Timeout for VISA Read Operations
        self.Instrument.opc_timeout = 5000  # Timeout for opc-synchronised operations
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
        """
        A function that sets up the measurements time, sends data to Arduino, and creates the threads for measurements and instrument control.
        """
        # Set up measurements time
        self.measurements_time = {'minutes': 0, 'seconds': 0, 'total_seconds': 0}
        temp = self.timeEdit.time()
        minutes = temp.minute()
        seconds = temp.second()
        self.measurements_time['minutes'] = minutes
        self.measurements_time['seconds'] = seconds
        self.measurements_time['total_seconds'] = minutes * 60 + seconds
        # Print and display measurements time
        formatted_time = f"{minutes:02d}:{seconds:02d}"
        self.textBrowser.append(f"Measurements time is set: {formatted_time}")
        # Send setup with measurments time to Arduino
        self.json_string = json.dumps(self.measurements_time)
        self.Device.write(self.json_string.encode())
        self.textBrowser.append(f'Sent measurements time to Arduino: {self.json_string}')
        # Create threads for measurements and instrument control
        # self.measurements_thread = MeasurmentsThread(self.Device)
        self.instrument_thread = InstrumentThread(self.Instrument, self.Device, seconds)
        self.instrument_thread.started.connect(self.start)
        self.instrument_thread.data_saved.connect(self.change2, QtCore.Qt.QueuedConnection)

    def start(self):
        print("Start")
        self.pushButtonStart.setDisabled(True)
        self.pushButtonStop.setDisabled(False)
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
        print("Stop Instrument Thread")
        self.instrument_thread.quit()
        self.instrument_thread.terminate = True


def main():
    app = QtWidgets.QApplication([])
    window = ExampleApp()
    window.show()
    app.exec()
main()


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