import sys
from PyQt6 import QtWidgets, uic

from MainWindow import Ui_MainWindow

from PyQt6.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt6.QtCore import QIODevice, pyqtSlot

from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression

#Globale Variablen
serialNumber = 0

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        
        self.list_available_ports()
        
        self.cb_baudRate.addItems(["150", "300", "600", "1200", "2400", "4800", "9600", "19200", "38400" ,"57600", "115200", "230400"])
        self.cb_dataBits.addItems(["5", "6", "7", "8"])
        self.cb_stopBits.addItems(["1", "1.5", "2"])
        self.cb_parityBit.addItems(["None", "Even", "Odd", "Mark", "Space"])

        self.cb_baudRate.setCurrentIndex(10)
        self.cb_dataBits.setCurrentIndex(3)
        self.cb_stopBits.setCurrentIndex(0)
        self.cb_parityBit.setCurrentIndex(0)

        self.btn_readPorts.clicked.connect(self.list_available_ports)
        self.btn_clearLog.clicked.connect(self.clear_log)

        # Regulärer Ausdruck für nur Ziffern
        regex = QRegularExpression("^\\d+$")
        validator = QRegularExpressionValidator(regex)

        self.tb_serialNumberRemote.setValidator(validator)
        self.tb_serialNumberRemote.setMaxLength(7)

        self.btn_setSerialNumber.clicked.connect(self.set_serial_number)
        self.btn_open.clicked.connect(self.send_open_cmd)

    # Funktion zum Löschen des Log-Fensters
    def clear_log(self):
        self.tb_logOutput.clear()

    # Funktion zum Finden und Anzeigen verfügbarer Ports
    def list_available_ports(self):
        ports = QSerialPortInfo.availablePorts()
        self.cb_serialPorts.clear()
        for port in ports:
            print(f"Name: {port.portName()}, Beschreibung: {port.description()}")
            self.tb_logOutput.append(f"Name: {port.portName()}, Beschreibung: {port.description()}")    
            self.cb_serialPorts.addItem(port.portName())

    def set_serial_number(self):
        global serialNumber
        serialNumber = self.tb_serialNumberRemote.text()
        
    def send_open_cmd(self):
        print("Serialnumner: ", serialNumber)

app = QtWidgets.QApplication(sys.argv)

window = MainWindow()

window.show()
app.exec()