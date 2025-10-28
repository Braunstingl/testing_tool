import sys
from PyQt6 import QtWidgets, uic

from MainWindow import Ui_MainWindow

from PyQt6.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt6.QtCore import QIODevice, QByteArray

from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression

from PyQt6.QtWidgets import QFileDialog

#Globale Variablen
serialNumber = 0

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        
        self.list_available_ports()
        self.btn_closeSerialPort.setEnabled(False)


        #ComboBoxen für Serielle-Schnittstelle mit Werten füllen
        self.cb_baudRate.addItems(["150", "300", "600", "1200", "2400", "4800", "9600", "19200", "38400" ,"57600", "115200", "230400"])
        self.cb_dataBits.addItems(["5", "6", "7", "8"])
        self.cb_stopBits.addItems(["1", "1.5", "2"])
        self.cb_parityBit.addItems(["None", "Even", "Odd", "Mark", "Space"])
        
        #Standardwerte der Comboboxen setzen
        self.cb_baudRate.setCurrentIndex(10)
        self.cb_dataBits.setCurrentIndex(3)
        self.cb_stopBits.setCurrentIndex(0)
        self.cb_parityBit.setCurrentIndex(0)

        #click-Events verbinden
        self.btn_readPorts.clicked.connect(self.list_available_ports)
        self.btn_connectSerialPort.clicked.connect(self.connect_serial_port)
        self.btn_closeSerialPort.clicked.connect(self.close_serial_port)
        
        
        self.btn_clearLog.clicked.connect(self.clear_log)
        self.btn_saveLog.clicked.connect(self.save_text_to_file)

        # QSerialPort-Objekt initialisieren
        self.serial_port = QSerialPort()
        self.serial_port.readyRead.connect(self.read_data)
               
        # Signal für eingehende Daten verbinden
        # Daten werden empfangen, wenn das 'readyRead'-Signal ausgelöst wird
        #self.serial_port.readyRead.connect(self.read_data)

        # Regulärer Ausdruck für nur Ziffern
        regex = QRegularExpression("^\\d+$")
        validator = QRegularExpressionValidator(regex)

        self.tb_serialNumberRemote.setValidator(validator)
        self.tb_serialNumberRemote.setMaxLength(7)

        self.btn_setSerialNumber.clicked.connect(self.set_serial_number)
        self.btn_open.clicked.connect(self.send_open_cmd)

    def connect_serial_port(self):
        selected_port = self.cb_serialPorts.currentText()
        baud_rate = int(self.cb_baudRate.currentText())
        data_bits = int(self.cb_dataBits.currentText())
        stop_bits = float(self.cb_stopBits.currentText())
        parity_bit = str(self.cb_parityBit.currentText())

        self.serial_port.setPortName(selected_port)   
        self.serial_port.setBaudRate(baud_rate)
        self.serial_port.setDataBits(QSerialPort.DataBits.Data8)
        self.serial_port.setParity(QSerialPort.Parity.NoParity)
        self.serial_port.setStopBits(QSerialPort.StopBits.OneStop)
        self.serial_port.setFlowControl(QSerialPort.FlowControl.NoFlowControl)

        if self.serial_port.open(QIODevice.OpenModeFlag.ReadWrite):
            self.tb_logOutput.append(f"Verbinde mit Port: {selected_port}, Baudrate: {baud_rate}, Datenbits: {data_bits}, Stoppbits: {stop_bits}, Paritätsbit: {parity_bit}")
            self.btn_connectSerialPort.setEnabled(False)
            self.btn_closeSerialPort.setEnabled(True)
        else:
            self.tb_logOutput.append(f"Fehler beim Öffnen des Ports: {selected_port}")
    
    def close_serial_port(self):
        if self.serial_port.isOpen():
            self.serial_port.close()
            self.tb_logOutput.append("Serieller Port geschlossen.")
            self.btn_connectSerialPort.setEnabled(True)
            self.btn_closeSerialPort.setEnabled(False)
        else:
            self.tb_logOutput.append("Der serielle Port ist nicht geöffnet.")

    def write_data(self, data: str):
            """Sendet Daten an den seriellen Port."""
            # Wichtig: String muss in Bytes konvertiert werden
            data_to_send = QByteArray(data.encode('utf-8'))
            self.serial_port.write(data_to_send)
            self.tb_logOutput.append(f"▶ Gesendet: {data}")

    def read_data(self):
        data_bytes = self.serial_port.readAll()
        raw_bytes = data_bytes.data()
        
        # 1. Konvertiere Rohdaten (Bytes) in einen Hex-String (z.B. "48656C6C6F")
        hex_string = raw_bytes.hex().upper()
        
        # 2. Füge Leerzeichen zur Lesbarkeit zwischen den Bytes ein (z.B. "48 65 6C 6C 6F")
        output_text = ' '.join(hex_string[i:i+2] for i in range(0, len(hex_string), 2))
        
        # 3. Füge einen Zeilenumbruch hinzu, um die Pakete visuell zu trennen
        self.tb_logOutput.append(f"<{output_text}>")


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
        self.write_data("ER_CMD#U?")
        self.read_data()

    def save_text_to_file(self):
            # 2. Dateidialog öffnen
            # getSaveFileName gibt einen Tupel zurück: (Dateipfad, Filter)
            file_path, _ = QFileDialog.getSaveFileName(self, "Datei speichern", 
                                                    "", "Textdateien (*.txt);;Alle Dateien (*)")

            if file_path:
                try:
                    # 3. Inhalt aus dem QTextBrowser abrufen
                    content = self.tb_logOutput.toPlainText() # Oder .toHtml()
                    
                    # 4. Inhalt in die Datei speichern
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"Datei erfolgreich gespeichert unter: {file_path}")
                except Exception as e:
                    print(f"Fehler beim Speichern der Datei: {e}")

app = QtWidgets.QApplication(sys.argv)

window = MainWindow()

window.show()
app.exec()