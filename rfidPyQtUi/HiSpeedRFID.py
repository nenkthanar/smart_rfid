
VERSION = "v1.0.0"
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QTextEdit, QWidget, QApplication, QVBoxLayout
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
import wx
import datetime,time
import os
app = wx.App(False)
width, height = wx.GetDisplaySize()

print("HiSpeed RFID User interface is running")

def check_port():
    port_list = []
    from serial.tools import list_ports
    ports = list_ports.comports()  # Outputs list of available serial ports
    for port in ports :
        port_list.append(port.name)
    return port_list 

print(check_port())
port_list = []
_check_port = check_port()
for i in range (0, len(_check_port)):
    port_list.append(_check_port[i])

baud_list = [115200,57600,38400,19200,14400,9600,7200,4800]

try:
    import Queue
except:
    import queue as Queue
import sys, time, serial
 
WIN_WIDTH, WIN_HEIGHT = 800, 700    # Window size
SER_TIMEOUT = 0.1                   # Timeout for serial Rx
RETURN_CHAR = "\n"                  # Char to be sent when Enter key pressed
PASTE_CHAR  = "\x16"                # Ctrl code for clipboard paste
baudrate    = 9600  
              # Default baud rate
try:
    portname  = port_list[0]    
except Exception as e:
    portname = "COM1"
                # Default port name
hexmode     = False                 # Flag to enable hex display
 
# Convert a string to bytes
def str_bytes(s):
    return s.encode('latin-1')
     
# Convert bytes to string
def bytes_str(d):
    return d if type(d) is str else "".join([chr(b) for b in d])
     
# Return hexadecimal values of data
def hexdump(data):
    return " ".join(["%02X" % ord(b) for b in data])
 
# Return a string with high-bit chars replaced by hex values
def textdump(data):
    return "".join(["[%02X]" % ord(b) if b>'\x7e' else b for b in data])
     
# Display incoming serial data
def display(s):
    if not hexmode:
        sys.stdout.write(textdump(str(s)))
    else:
        sys.stdout.write(hexdump(s) + ' ')

def getDate():
      x = datetime.datetime.now()
      return x.day + x.month + x.year

def checkExistData():
    path = "exist/static/data"
    if not os.path.exists(path):
        
        os.makedirs(path)
        f = open(path + "date.txt","w")
        f.write(str(getDate()))
        f.close()
        return
    
    da = open(path + "date.txt","r")
    db = da.read()
    d0 = int(getDate())
    d1 = int(db)
    diff = d0 - d1
    remain = 30 - diff
    print("Remain date:",remain)
    if remain == 0:
        print("End of evaluation")
        time.sleep(5)
        sys.exit()
    return remain

remain = checkExistData()

class MyTextBox(QTextEdit):
    def __init__(self, *args): 
        QTextEdit.__init__(self, *args)

    def keyPressEvent(self, event):   
        self.parent().keypress_handler(event)
 

# Main widget            
class MyWidget(QWidget):
    text_update = QtCore.pyqtSignal(str)
    global port_list,baud_list,baudrate,portname
    def __init__(self, *args): 
        QWidget.__init__(self, *args)
        self.writeData = []
        self.readBlock = 0
        self.sector = 'A'
        self.font = QtGui.QFont()
        self.font.setFamily("Courier New")           # Monospaced font
        self.font.setPointSize(10)
        self.resize(1000, 800)      # Set window size
        self.text_update.connect(self.append_text)      # Connect text update to handler
        sys.stdout = self 
        self.UiComponents()                               # Redirect sys.stdout to self

    def serialStart(self):
        baudrate = int(float(self.cmbBaud.currentText()))
        portname = str(self.cmbPort.currentText())
        self.serth = SerialThread(portname, baudrate)   # Start serial thread
        self.serth.start()
        self.btnConn.setText("DISCONNECT") 
        self.btnConn.setStyleSheet("background-color : rgb(57, 255, 51 );height:30px;width:90px;border-radius:3px;color:blue;") 

    def serialStop(self):
        self.serth.stop()
        print("[App]:> Serial stop")
        self.btnConn.setText("CONNECT") 
        self.btnConn.setStyleSheet("background-color : rgb(133, 193, 233);height:30px;width:90px;border-radius:3px;color:blue;") 

    def onselectedBaud(self):
        baudrate = int(float(self.cmbBaud.currentText()))
        print("[App]:> baudrate:",baudrate)

    def onselectedPort(self):
        portname = str(self.cmbPort.currentText())
        print("[App]:> portname:",portname)

    def serialConn(self):
        if self.btnConn.text() == "CONNECT":
           self.serialStart()
        else :
           self.serialStop()

    def onselectedSector(self):
        self.sector = str(self.cmbSector.currentText())
        print(self.sector)

    def eventFilter(self,obj,event):
        pass
        num = len(self.writetxt.toPlainText())
        self.curlbl.setText(str(num) + ' Bytes')
        return QWidget.eventFilter(self, obj, event)

    def terminalGroup(self):
        groupBox = QGroupBox("TERMINAL GROUP")
        self.textbox = MyTextBox(self)  # Create wcustom text box
        self.textbox.setFont(self.font)
        self.textbox.setStyleSheet("background-color:rgb(128,128,128);border-radius:5px;color:white;font-size:15px;font-weight:bold;") 

        self.btnConn = QPushButton("CONNECT",self)
        self.btnConn.clicked.connect(self.serialConn)
        self.btnConn.setStyleSheet("background-color : rgb(133, 193, 233);height:30px;width:90px;border-radius:3px;color:blue;") 

        self.btnTest = QPushButton("TEST",self) 
        self.btnTest.clicked.connect(self.testConn)
        self.btnTest.setStyleSheet("background-color : gray;height:30px;width:90px;border-radius:3px;color:white;") 

        self.portlbl = QLabel(self)
        self.portlbl.setText('PORT')
        self.baudlbl = QLabel(self)
        self.baudlbl.setText('BAUDRATE')
  
        self.cmbPort = QComboBox(self)
        for i in range(0,len(port_list)):
            self.cmbPort.addItem(port_list[i])
        self.cmbPort.currentIndexChanged.connect(self.onselectedPort)
        self.cmbPort.setStyleSheet("height:30px;width:80px;border-radius:3px;font-weight:bold")

        self.cmbBaud = QComboBox(self)
        for i in range(0,len(baud_list)):
             self.cmbBaud.addItem(str(baud_list[i]))
        self.cmbBaud.currentIndexChanged.connect(self.onselectedBaud)
        self.cmbBaud.setStyleSheet("height:30px;width:80px;border-radius:3px;font-weight:bold")

        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        vbox = QVBoxLayout()
        hbox1.addWidget(self.portlbl)
        hbox1.addWidget(self.cmbPort)
        hbox1.addWidget(self.baudlbl)
        hbox1.addWidget(self.cmbBaud)
        hbox1.addStretch(0)
        vbox.addLayout(hbox1)
        hbox2.addWidget(self.btnConn)
        hbox2.addWidget(self.btnTest)
        vbox.addWidget(self.textbox,1)
        vbox.addStretch(0)
        hbox2.addStretch(0)
        vbox.addLayout(hbox2)
        groupBox.setLayout(vbox)
        return groupBox

    def writeGroup(self):
        groupBox = QGroupBox("WRITE GROUP")
        self.maxlbl = QLabel(self)
        self.maxlbl.setText("MAXIMUN")
        self.maxlbl.setStyleSheet("color:red;font-size:11px;font-weight:bold") 
        self.maxval = QLabel(self)
        self.maxval.setText("16")

        self.numlbl = QLabel(self)
        self.numlbl.setText("CURRENT")

        self.curlbl = QLabel(self)
        self.curlbl.setText("0")
        self.curlbl.setStyleSheet("color:red;font-size:18px;font-weight:bold") 

        self.writetxt = QTextEdit(self)
        self.writetxt.setFont(self.font)
        self.writetxt.installEventFilter(self)
        self.writetxt.setStyleSheet("background-color : white;border-radius:5px;color:black;font-size:20px;font-weight:bold") 

        self.btnSend = QPushButton("WRITE",self)
        self.btnSend.clicked.connect(self.rfidWrite)
        self.btnSend.setStyleSheet("background-color : gray;height:30px;width:90px;border-radius:3px;color:white") 

        self.btnRead = QPushButton("READ",self)
        self.btnRead.clicked.connect(self.rfidRead)
        self.btnRead.setStyleSheet("background-color : green;height:30px;width:90px;border-radius:3px;color:white") 

        self.stWlbl = QLabel(self)
        self.stWlbl.setText('WRITE BLOCK')

        self.stRlbl = QLabel(self)
        self.stRlbl.setText('READ BLOCK')

        self.numRead = QLabel(self)
        self.numRead.setText('BLOCK COUNT')

        self.sectorlbl = QLabel(self)
        self.sectorlbl.setText('SECTOR')

        self.cmbStartWrite = QComboBox(self)
        for i in range(0,16):
             self.cmbStartWrite.addItem(str(i))
        self.cmbStartWrite.setStyleSheet("height:30px;width:80px;border-radius:3px;font-weight:bold")
        
        self.cmbStartRead = QComboBox(self)
        for i in range(0,16):
             self.cmbStartRead.addItem(str(i))
        self.cmbStartRead.setStyleSheet("height:30px;width:80px;border-radius:3px;font-weight:bold")

        self.cmbEndRead = QComboBox(self)
        for i in range(0,16):
             self.cmbEndRead.addItem(str(i))
        self.cmbEndRead.setStyleSheet("height:30px;width:80px;border-radius:3px;font-weight:bold")
        
        self.cmbSector = QComboBox(self)
        self.cmbSector.addItem('A')
        self.cmbSector.addItem('B')
        self.cmbSector.currentIndexChanged.connect(self.sectorSelected)
        self.cmbSector.setStyleSheet("height:30px;width:80px;border-radius:3px;font-weight:bold")
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        vbox = QVBoxLayout()

        hbox1.addWidget(self.sectorlbl)
        hbox1.addWidget(self.cmbSector)
        hbox1.addWidget(self.stRlbl)
        hbox1.addWidget(self.cmbStartRead)
        hbox1.addWidget(self.stWlbl)
        hbox1.addWidget(self.cmbStartWrite)
        hbox1.addWidget(self.numRead)
        hbox1.addWidget(self.cmbEndRead)

        hbox1.addStretch(0)
        vbox.addLayout(hbox1)
        vbox.addWidget(self.writetxt)
        hbox2.addWidget(self.btnSend)
        hbox2.addWidget(self.btnRead)
        hbox2.addWidget(self.maxlbl)
        hbox2.addWidget(self.maxval)
        hbox2.addWidget(self.numlbl)
        hbox2.addWidget(self.curlbl)
        hbox2.addStretch(0)
        vbox.addLayout(hbox2)
        groupBox.setLayout(vbox)
        return groupBox

    def UiComponents(self):
        self.grid = QGridLayout(self)
        self.grid.addWidget(self.terminalGroup(), 0, 0)
        self.grid.addWidget(self.writeGroup(), 1, 0)
        self.show() 

    def testConn(self):
        self.serth.ser_out("T?") 

    def rfidRead(self):
        self.reads = 'R'+ self.cmbStartRead.currentText() + '?'
        self.serth.ser_out(self.reads) 

    def rfidWrite(self):
        startBlock = self.cmbStartWrite.currentText()
        if len(startBlock) > 1:
           self.data = 'W' + self.cmbStartWrite.currentText() + self.writetxt.toPlainText() + '?'
        else:
           self.data = 'W' + '0' + self.cmbStartWrite.currentText() + self.writetxt.toPlainText() + '?' 
        self.serth.ser_out(self.data) 

    def sectorSelected(self):
        sector = 'S'+ self.cmbSector.currentText() + '?'
        self.serth.ser_out(sector) 
        #print(sector)

    def write(self, text):                      
        self.text_update.emit(text)            
         
    def flush(self):                            
        pass
 
    def append_text(self, text):                
        cur = self.textbox.textCursor()
        cur.movePosition(QtGui.QTextCursor.End) # Move cursor to end of text
        s = str(text)
        while s:
            head,sep,s = s.partition("\n")      # Split line at LF
            cur.insertText(head)                # Insert text at cursor
            if sep:                             # New line if LF
                cur.insertBlock()
        self.textbox.setTextCursor(cur)         # Update visible cursor
 
    def keypress_handler(self, event):          # Handle keypress from text box
        k = event.key()
        s = RETURN_CHAR if k==QtCore.Qt.Key_Return else event.text()
        if len(s)>0 and s[0]==PASTE_CHAR:       # Detect ctrl-V paste
            cb = QApplication.clipboard() 
            self.serth.ser_out(cb.text())       # Send paste string to serial driver
        else:
            self.serth.ser_out(s)               # ..or send keystroke
     
    def closeEvent(self, event):                # Window closing
        self.serth.running = False              # Wait until serial thread terminates
        self.serth.wait()
         
# Thread to handle incoming & outgoing serial data
class SerialThread(QtCore.QThread):
    def __init__(self, portname, baudrate): 
        QtCore.QThread.__init__(self)
        self.portname, self.baudrate = portname, baudrate
        self.txq = Queue.Queue()
        self.running = True
 
    def ser_out(self, s):                   # Write outgoing data to serial port if open
        self.txq.put(s)                     # ..using a queue to sync with reader thread
         
    def ser_in(self, s):                    # Write incoming serial data to screen
        display(s)
        
    def stop(self):
        self.running = False

    def run(self):                          # Run serial reader thread
        print("[App]:> Opening %s at %u baud %s" % (self.portname, self.baudrate,
              "(hex display)" if hexmode else ""))
        try:
            self.ser = serial.Serial(self.portname, self.baudrate, timeout=SER_TIMEOUT)
            time.sleep(SER_TIMEOUT*1.2)
            self.ser.flushInput()
        except:
            self.ser = None
        if not self.ser:
            print("[App]:> Can't open port")
            self.running = False
        while self.running:
            s = self.ser.read(self.ser.in_waiting or 1)
            if s:                                       # Get data from serial port
                self.ser_in(bytes_str(s))               # ..and convert to string
            if not self.txq.empty():
                txd = str(self.txq.get())               # If Tx data in queue, write to serial port
                self.ser.write(str_bytes(txd))
        if self.ser:                                 
            self.ser.close()
            self.ser = None
 

if __name__ == "__main__":
    app = QApplication(sys.argv) 
    opt = err = None
    for arg in sys.argv[1:]:                # Process command-line options
        if len(arg)==2 and arg[0]=="-":
            opt = arg.lower()
            if opt == '-x':                 # -X: display incoming data in hex
                hexmode = True
                opt = None
        else:
            if opt == '-b':                 # -B num: baud rate, e.g. '9600'
                try:
                    baudrate = int(arg)
                except:
                    err = "Invalid baudrate '%s'" % arg
            elif opt == '-c':               # -C port: serial port name, e.g. 'COM1'
                portname = arg
    if err:
        print(err)
        sys.exit(1)
        
    wi = MyWidget()
    wi.setWindowTitle('HiSpeed RFID READER  ' + VERSION +"( Evaluate for " + str(remain) + ")")
    wi.show() 
    sys.exit(app.exec_())