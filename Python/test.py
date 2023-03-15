import sys
import time
import json

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTextEdit, QVBoxLayout

import visa
import serial

class ZVAThread(QObject):
    measurement_complete = pyqtSignal(str)

    def __init__(self, visa_address, parent=None):
        super().__init__(parent)
        self.visa_address = visa_address
        self.zva = visa.ResourceManager().open_resource(self.visa_address)

    @pyqtSlot(str)
    def start_measurement(self, temperature):
        self.zva.write(f'MEASURE:SCALAR {temperature}')
        self.zva.query('*OPC?')
        filename = f'{temperature}_measurement.csv'
        self.zva.write(f'MMEM:STOR:TRAC:CHAN 1, "{filename}"')
        self.measurement_complete.emit(filename)

class ArduinoThread(QObject):
    temperature_ready = pyqtSignal(str)

    def __init__(self, port, parent=None):
        super().__init__(parent)
        self.port = port
        self.arduino = serial.Serial(self.port, 9600, timeout=1)

    def run(self):
        while True:
            rule = json.loads(self.arduino.readline().decode('utf-8'))
            temperature = rule['temperature']
            self.temperature_ready.emit(temperature)
            time.sleep(rule['delay'])

class MeasurementApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.zva_thread = ZVAThread('GPIB0::1::INSTR')
        self.arduino_thread = ArduinoThread('/dev/ttyACM0')

        self.start_button = QPushButton('Start Measurement')
        self.start_button.clicked.connect(self.start_measurement)

        self.log_output = QTextEdit()

        layout = QVBoxLayout()
        layout.addWidget(self.start_button)
        layout.addWidget(self.log_output)

        self.setLayout(layout)

        self.arduino_thread.temperature_ready.connect(self.zva_thread.start_measurement)
        self.zva_thread.measurement_complete.connect(self.log_measurement_complete)

    def start_measurement(self):
        self.log_output.append('Starting measurement...')
        rule = {'temperature': '25C', 'delay': 30}
        self.arduino_thread.arduino.write(json.dumps(rule).encode('utf-8'))

    @pyqtSlot(str)
    def log_measurement_complete(self, filename):
        self.log_output.append(f'Measurement complete, saved to {filename}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    measurement_app = MeasurementApp()
    measurement_app.show()
    sys.exit(app.exec_())
