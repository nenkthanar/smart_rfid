
VERSION = "v1.0.0"
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QTextEdit, QWidget, QApplication, QVBoxLayout
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
import wx
from SL025 import *

app = wx.App(False)
width, height = wx.GetDisplaySize()
print( "Screen resolution = >",width,height)

def check_port():
    port_list = []
    from serial.tools import list_ports
    ports = list_ports.comports()  # Outputs list of available serial ports
    for port in ports :
        port_list.append(port.name)
    return port_list 

print(check_port())
port_list = ["COM1"]
_check_port = check_port()
for i in range (0, len(_check_port)):
    port_list.append(_check_port[i])

baud_list = [12800,115200,57600,38400,19200,14400,9600,7200,4800,2400,1800,1200,600,300,150,134,110,75]

try:
    import Queue
except:
    import queue as Queue
import sys, time, serial
 
WIN_WIDTH, WIN_HEIGHT = 800, 700    # Window size
SER_TIMEOUT = 0.1                   # Timeout for serial Rx
RETURN_CHAR = "\n"                  # Char to be sent when Enter key pressed
PASTE_CHAR  = "\x16"                # Ctrl code for clipboard paste
baudrate    = 9600                # Default baud rate
try:
    portname    = port_list[0]    
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
 
# Custom text box, catching keystrokes
class MyTextBox(QTextEdit):
    global width,height
    def __init__(self, *args): 
        QTextEdit.__init__(self, *args)
        self.setFixedWidth(width/2 - 400)
        self.setFixedHeight(height - 500)

    def keyPressEvent(self, event):     # Send keypress to parent's handler
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
        self.textbox = MyTextBox()  # Create wcustom text box
        self.font = QtGui.QFont()
        self.font.setFamily("Courier New")           # Monospaced font
        self.font.setPointSize(10)
        self.textbox.setFont(self.font)
        layout = QVBoxLayout()
        layout.addWidget(self.textbox)
      
        self.setLayout(layout)
        self.resize(WIN_WIDTH, WIN_HEIGHT)      # Set window size
        self.text_update.connect(self.append_text)      # Connect text update to handler
        sys.stdout = self 
        self.UiComponents()                               # Redirect sys.stdout to self

    def serialStart(self):
        baudrate = int(float(self.cmbBaud.currentText()))
        portname = str(self.cmbPort.currentText())
        self.serth = SerialThread(portname, baudrate)   # Start serial thread
        self.serth.start()
        self.btnConn.setText("DISCONNECT") 

    def serialStop(self):
        self.serth.terminate()
        print("[App]:> Serial stop")
        self.btnConn.setText("CONNECT") 

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

    def UiComponents(self): 
        self.cmbPort = QComboBox(self)
        for i in range(0,len(port_list)):
            self.cmbPort.addItem(port_list[i])
        self.cmbPort.setStyleSheet("text-align: center;")
        self.cmbPort.setGeometry(width/2 - 145, 16, 80, 38) 
        self.cmbPort.currentIndexChanged.connect(self.onselectedPort)

        self.cmbBaud = QComboBox(self)
        for i in range(0,len(baud_list)):
             self.cmbBaud.addItem(str(baud_list[i]))
        self.cmbBaud.setStyleSheet("text-align: center;")
        self.cmbBaud.setGeometry(width/2 - 60, 16, 80, 38) 
        self.cmbBaud.currentIndexChanged.connect(self.onselectedBaud)
       
        self.btnConn = QPushButton("CONNECT",self)
        self.btnConn.setGeometry(width/2 - 300,15,150,40)#(pos_X,pos_Y,size_w,size_h) vertical space 45 px
        self.btnConn.clicked.connect(self.serialConn)
        
        self.btnLogin = QPushButton("LOGIN",self)
        self.btnLogin.setGeometry(width/2 - 300,60,150,40)#(pos_X,pos_Y,size_w,size_h)  
        self.btnLogin.clicked.connect(self.rfidLogin)

        self.cmbSector = QComboBox(self)
        self.cmbSector.addItem('A')
        self.cmbSector.addItem('B')
        self.cmbSector.setStyleSheet("text-align: center;")
        self.cmbSector.setGeometry(width/2 - 145, 61, 80, 38) 
        self.cmbSector.currentIndexChanged.connect(self.onselectedSector)

        self.btnSend = QPushButton("WRITE",self)
        self.btnSend.setGeometry(width/2 - 300,105,150,40)#(pos_X,pos_Y,size_w,size_h)  
        self.btnSend.clicked.connect(self.rfidWrite)

        self.btnRead = QPushButton("READ",self)
        self.btnRead.setGeometry(width/2 - 300,150,150,40)#(pos_X,pos_Y,size_w,size_h)  
        self.btnRead.clicked.connect(self.rfidRead)

        self.cmbStartWrite = QComboBox(self)
        for i in range(0,16):
             self.cmbStartWrite.addItem(str(i))
        self.cmbStartWrite.setStyleSheet("text-align: center;")
        self.cmbStartWrite.setGeometry(width/2 - 145 , 106, 80, 38) 

        self.cmbStartRead = QComboBox(self)
        for i in range(0,16):
             self.cmbStartRead.addItem(str(i))
        self.cmbStartRead.setStyleSheet("text-align: center;")
        self.cmbStartRead.setGeometry(width/2 - 145 , 151, 80, 38) 
       
        self.cmbEndRead = QComboBox(self)
        for i in range(0,16):
             self.cmbEndRead.addItem(str(i))
        self.cmbEndRead.setStyleSheet("text-align: center;")
        self.cmbEndRead.setGeometry(width/2 - 60 , 151, 80, 38) 

        self.writetxt = QTextEdit(self)
        self.writetxt.setGeometry(width/2 + 300 ,15,400,180)
        self.writetxt.setFont(self.font)
        self.showMaximized() 

    def testConn(self):
        self.serth.ser_out("Connection is OK?") 

    def rfidLogin(self):
        RFID.login(self.serth,str(self.cmbSector.currentText()))

    def rfidRead(self):
        RFID.read(self.serth,self.cmbStartRead.currentText(),self.cmbEndRead.currentText())

    def rfidWrite(self):
        startBlock = self.cmbStartWrite.currentText()
        if len(startBlock) > 1:
           self.data = 'W' + self.cmbStartWrite.currentText() + self.writetxt.toPlainText() + '?'
        else:
           self.data = 'W' + '0' + self.cmbStartWrite.currentText() + self.writetxt.toPlainText() + '?' 
        self.serth.ser_out(self.data) 

    def send(self):
        self.serth.ser_out("test?") 

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
        try:
           self.ser.close()
           self.ser = None
        except Exception as e:
           pass

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
    w = MyWidget()
    w.setWindowTitle('GENERAL PROPOSE RFID READER  ' + VERSION)
    w.show() 
    sys.exit(app.exec_())