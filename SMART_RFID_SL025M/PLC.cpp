#include "PLC.h"

//> Read data from PLC ------------------------------------
void PLC::PLCread(String adr, byte len) // length is from 0-255
{
  byte PLCcmdREAD[20];
  
  //start of packet -----
  PLCcmdREAD[0]= 0x40;
  PLCcmdREAD[1]= 0x30;
  PLCcmdREAD[2]= 0x30;

  //command RD/WD
  PLCcmdREAD[3]= (byte)'R'; 
  PLCcmdREAD[4]= (byte)'D';

  //Start address
  PLCcmdREAD[5]= (byte)adr.charAt(0);
  PLCcmdREAD[6]= (byte)adr.charAt(1);
  PLCcmdREAD[7]= (byte)adr.charAt(2);
  PLCcmdREAD[8]= (byte)adr.charAt(3);

  //adding data which is the length of reading
  PLCcmdREAD[9] = 48; //"0"
  PLCcmdREAD[10] = (int)((float)len/100)%10 + 48;  
  PLCcmdREAD[11] = (int)((float)len/10)%10 + 48; 
  PLCcmdREAD[12] = (int)((float)len/1)%10 + 48;    

  byte checksum = PLCchecksum(PLCcmdREAD,13);
  PLCcmdREAD[13]   = (checksum>>4 & 0x0F) + 48; //change to Ascii
  PLCcmdREAD[14]   = (checksum    & 0x0F) + 48; //change to Ascii  

  //end of packet
  PLCcmdREAD[15]= 0x2A;
  PLCcmdREAD[16]= 0x0D;

  //Serial.println();
  //Serial.print(">> Read PLC command packet = ");
  //print_byte_array(PLCcmdREAD,17);
  Serial.println(); 

  writeByte(PLCcmdREAD,17);  
  
  delay (50); //wait for response from PLC
  zero_byte_array(PLCreadData,60); //clear array
  
  if (availableSerial()>0) //now bufferring in PLCreadData[]
  {
    for (int i=0;i<60;i++)
      {
         PLCreadData[i]=readByte();
      }
  }

  //Serial.print(">> PLC data readback rd..");
  //print_byte_array(PLCreadData,60); 
  //Serial.println();
  
}


//> write data to PLC belt conveyer ----------------------------
void PLC::PLCwrite(byte* data, String adr, byte len) //
{
  byte PLCcmdWRITE[60];
  
  //start of packet -----
  PLCcmdWRITE[0]= 0x40;
  PLCcmdWRITE[1]= 0x30;
  PLCcmdWRITE[2]= 0x30;

  //command RD/WD
  PLCcmdWRITE[3]= (byte)'W'; 
  PLCcmdWRITE[4]= (byte)'D';

  //Start address
  PLCcmdWRITE[5]= (byte)adr.charAt(0);
  PLCcmdWRITE[6]= (byte)adr.charAt(1);
  PLCcmdWRITE[7]= (byte)adr.charAt(2);
  PLCcmdWRITE[8]= (byte)adr.charAt(3);

  //byte * dummy;
  int offset = 9;
  int i = 0;
  
  //Adding LineID [0][1] Tag[2][3] SectionID[4][5][6][7] => len should be 8
  for (i=0; i<len; i++)
  {
    byte2plcword((byte)data[i]); //output is at byteDummy[]
    PLCcmdWRITE[offset+i*2+0] = (byte)byteDummy[0];
    PLCcmdWRITE[offset+i*2+1] = (byte)byteDummy[1];
  }

  offset = offset+i*2; //update a new offset
  
  byte checksum = PLCchecksum(PLCcmdWRITE,offset);
  //Serial.print("Checksum = "); Serial.println (checksum, HEX);
  byte2plcword(checksum);
  PLCcmdWRITE[offset+0] = byteDummy[0];
  PLCcmdWRITE[offset+1] = byteDummy[1];
    
  //PLCcmdWRITE[offset+i+4] = x ; //(checksum>>4 & 0x0F) + 48; //change to Ascii
  //PLCcmdWRITE[offset+i+5] = y ; //(checksum    & 0x0F) + 48; //change to Ascii  

  //end of packet
  PLCcmdWRITE[offset+2]= 0x2A;
  PLCcmdWRITE[offset+3]= 0x0D;

  Serial.print(">> Write PLC command packet = ");
  //print_byte_array(PLCcmdWRITE,offset+4); 
  Serial.println();

  writeByte(PLCcmdWRITE,offset+4);  
  Serial.println("Command Write Check");
  delay (50); //wait for response from PLC
  zero_byte_array(PLCreadData,60); //clear array
  
  if (availableSerial()>0) //now bufferring in PLCreadData[]
  {
    for (int i=0;i<60;i++)
      {
         PLCreadData[i]=readByte();
      }
  }

  Serial.print (">> PLC data readback wr..");
  print_byte_array(PLCreadData,20); 
  Serial.println();
  
}

//read rf id tag via PLC
bool PLC::readRFID_PLC(String addr, byte *data, byte bSize, byte numword){
  PLCread(addr, numword);    //read from PLC @0000

  int length = numword*4;

  //check response frame format (End Code)
  byte endcode = (char2int((char)PLCreadData[5])<<4)|char2int((char)PLCreadData[6]);
  if(endcode == 0x00){
    //check sum error
    byte checksum = PLCchecksum(PLCreadData,7+length);
    byte2plcword(checksum);
    if( (byteDummy[0] == PLCreadData[7+length]) && (byteDummy[1] == PLCreadData[7+length+1]) ){
      //Serial.println("PLC FCS OK");
      for(int i=0; i<bSize; i++){
        data[i] = (char2int((char)PLCreadData[2*i+7])<<4)|char2int((char)PLCreadData[2*i+7+1]);
      }

      //Check repeat read RFID
      if( memcmp(previousRFBuffer, data, sizeof(previousRFBuffer)) == 0 ){
        Serial.println("Ignore this card(same data...)");Serial.println();
        return false;
      }else{
        memcpy(previousRFBuffer, data, sizeof(previousRFBuffer));
      }

      Serial.print("PLC RFID: ");print_byte_array(data, bSize);Serial.println();
      return true;
    }else{
      Serial.println("PLC FCS Wrong");
      return false;
    }

  }else if(endcode == 0x13){
    Serial.println("PLC:FCS error");
    return false;
  }else if(endcode == 0x14){
    Serial.println("PLC:Format error");
    return false;
  }else if(endcode == 0x15){
    Serial.println("PLC:Entry number data error");
    return false;
  }else if(endcode == 0x18){
    Serial.println("PLC:Frame length error");
    return false;
  }else if(endcode == 0x21){
    Serial.println("PLC:CPU error");
    return false;
  }

  return false;

}

bool PLC::readAddress_PLC(String addr, byte *data, byte bSize, byte numword)
{

  PLCread(addr, numword);    //read from PLC @0000

  int length = numword*4;

  //check response frame format (End Code)
  byte endcode = (char2int((char)PLCreadData[5])<<4)|char2int((char)PLCreadData[6]);
  if(endcode == 0x00){
    //check sum error
    byte checksum = PLCchecksum(PLCreadData,7+length);
    byte2plcword(checksum);
    if( (byteDummy[0] == PLCreadData[7+length]) && (byteDummy[1] == PLCreadData[7+length+1]) ){
      //Serial.println("PLC FCS OK");
      for(int i=0; i<bSize; i++){
        data[i] = (char2int((char)PLCreadData[2*i+7])<<4)|char2int((char)PLCreadData[2*i+7+1]);
      }

      Serial.print("PLC @");Serial.print(addr);Serial.print(": ");
      print_byte_array(data, bSize);Serial.println();
      return true;
    }else{
      Serial.print("PLC @");Serial.print(addr);Serial.print(": ");
      Serial.println("PLC FCS Wrong");
      return false;
    }

  }else if(endcode == 0x13){
    Serial.print("PLC @");Serial.print(addr);Serial.print(": ");
    Serial.println("PLC:FCS error");
    return false;
  }else if(endcode == 0x14){
    Serial.print("PLC @");Serial.print(addr);Serial.print(": ");
    Serial.println("PLC:Format error");
    return false;
  }else if(endcode == 0x15){
    Serial.print("PLC @");Serial.print(addr);Serial.print(": ");
    Serial.println("PLC:Entry number data error");
    return false;
  }else if(endcode == 0x18){
    Serial.print("PLC @");Serial.print(addr);Serial.print(": ");
    Serial.println("PLC:Frame length error");
    return false;
  }else if(endcode == 0x21){
    Serial.print("PLC @");Serial.print(addr);Serial.print(": ");
    Serial.println("PLC:CPU error");
    return false;
  }

  return false;
}

// bool PLC::readAlarm_PLC()
// {

//   return true;
// }

// bool PLC::readState_PLC()
// {

//   return true;
// }

//> find checksum bytes -----------------------------------------------
byte PLC::PLCchecksum(byte * data, int len)
{
  byte dummy=0;
  for (int i=0; i<len; i++)
  {
    dummy = dummy ^ data[i];
  }
  return (dummy);
  
}

void PLC::print_byte_array(byte *buffer, byte bufferSize) {
    for (byte i = 0; i < bufferSize; i++) {
        Serial.print(buffer[i] < 0x10 ? " 0" : " ");
        Serial.print(buffer[i], HEX);
    }
}


void PLC::zero_byte_array(byte *buffer, byte bufferSize) {
    for (byte i = 0; i < bufferSize; i++) {
         buffer[i]= 0x00;
    }
}

String PLC::bytes2string(byte *buffer, byte idx, byte len) {
  String dummy = ""; 
    for (byte i = 0; i < len; i++) {
         dummy = dummy + String((char)buffer[idx+i]); //String((char *)byteArray)
         //Serial.println(dummy);
    }
    return(dummy);
}

String PLC::plcword2string(byte *buffer, byte idx, byte wordcnt) {
  String dummy = ""; 
  byte newbyte;
  char c0,c1;
  int i;

  for (i = 0; i < wordcnt; i++) 
  {

     c0 = (char)(buffer[idx+i*2+0]);  
     c1 = (char)(buffer[idx+i*2+1]);     
 
     newbyte = 16*char2int(c0) + char2int(c1);

     dummy = dummy+String((char)newbyte);

     sprintf(cbuff, ">> plcword to string....@%d c0=%c c1=%c newbyte=%X \n",i,c0,c1,newbyte);
     Serial.print(cbuff);      
  }

  Serial.println (dummy);
  Serial.println();
  
  return(dummy);
}


int PLC::char2int(char c)
{
  int x;
  switch (c)
  {
    case '0': x=0; break;
    case '1': x=1; break;
    case '2': x=2; break;
    case '3': x=3; break;
    case '4': x=4; break;
    case '5': x=5; break;
    case '6': x=6; break;
    case '7': x=7; break;
    case '8': x=8; break;
    case '9': x=9; break;
    case 'A': x=10; break;
    case 'B': x=11; break;
    case 'C': x=12; break;
    case 'D': x=13; break;
    case 'E': x=14; break;
    case 'F': x=15; break;
    default : x=0; break;   
  }
  return(x);
}

void PLC::byte2plcword(byte k) //byte => plc word, e.g.  k=0x41 => dummy = {0x34, 0x31}
{
  byte x = (k>>4 & 0x0F) + 48; if (x>57) x = x+7; //0-9 or A-F 
  byte y = (k>>0 & 0x0F) + 48; if (y>57) y = y+7;
  byteDummy[0] = x;
  byteDummy[1] = y;
}


void PLC::char2plcword(char c) //char => plc word, e.g. "A"..k=0x41 => dummy = {0x34, 0x31}
{
  byte k = (int)(c);
  byte x = (k>>4 & 0x0F) + 48; if (x>57) x = x+7; //0-9 or A-F 
  byte y = (k>>0 & 0x0F) + 48; if (y>57) y = y+7;
  byteDummy[0] = x;
  byteDummy[1] = y;

}

void PLC::setSerial(Stream &streamObject){
    _serial = &streamObject;
}
    
void PLC::sendText(char *Text){
    _serial->println(Text);
}

void PLC::begin(Stream &serial) {
	_serial = &serial;
}

bool PLC::availableSerial() {
	return _serial->available();
}

uint8_t PLC::readByte() {
	return _serial->read();
} 

void PLC::flushSerial() {
	_serial->flush();
} 

void PLC::writeByte(uint8_t val) {
	_serial->write(val);
}

void PLC::writeByte(uint8_t val[], uint8_t len) {
  for(uint8_t i=0; i<len; i++)
	  _serial->write(val[i]);
}

