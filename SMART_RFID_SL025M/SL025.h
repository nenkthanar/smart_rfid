#define SEND_HEADER 0xBA
#define OPERATION_OK 0x00
#define NO_TAG 0x01
#define READ_FAIL 0x04
#define WRITE_FAIL 0x05

#define LOGIN_SUCCEED 0x02
#define LOGIN_FAIL 0x03
unsigned char flag_read=0,pv_flag_read=1;
byte rfidBuffer[16] = {};
//--------------- RFID Card Reader ---------------------
#define   CHK_BYTE1    0x04
#define   CHK_BYTE2    0x99
#define   IDX_CHK_BYTE1   1
#define   IDX_CHK_BYTE2   15 

//--------------- XBee network Communication -----------
byte HEADER,LEN,CMD,STATUS,UID[8],TYPE,CHKSUM,BOX,AFI,DSFID;

  bool read_state =  false;
  String rfidbuffer = "";
  String check_repeat = "";

 byte checksum(byte (*values),int length){
   byte result = values[0];
   for (int i = 1; i < length; i++)
   result ^= values[i];
   return result;
 }

byte RFID_login(){
     byte LoginSector0[]= {0xBA,0x0A,0x02,0x00,0xAA,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,checksum(LoginSector0,11)};  
     byte LoginSector1[]= {0xBA,0x0A,0x02,0x01,0xAA,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,checksum(LoginSector1,11)};  
     Serial1.write(LoginSector1,sizeof(LoginSector1));
     while(1){
      int c = Serial1.read();
      if (c == 0xBD) break;
      }
      while (Serial1.available()==0);    
      LEN = Serial1.read();
      while (Serial1.available()==0);   
      CMD = Serial1.read();
      while (Serial1.available()==0) ;   
      STATUS = Serial1.read();
      return STATUS;
      }
     
int readBlock(int startblock,int number,byte storedata[9]){
        byte *frame;
        frame = (byte *) malloc(5 * sizeof(byte));
        frame[0] = 0xBA;
        frame[1] = 3;
        frame[2] = 0x03;
        frame[3] = 0x04;
        frame[4] = checksum(frame, 4); 
         Serial1.write(frame, 5);
        free(frame);
        frame = NULL;
      while (1){    
      while (Serial1.available()==0); 
      if(Serial1.read() == 0xBD) break;
         }     
      while (Serial1.available()==0);    
         LEN = Serial1.read();
      while (Serial1.available()==0);   
         CMD = Serial1.read();
      while (Serial1.available()==0) ;   
         STATUS = Serial1.read();
      if (STATUS == 0x00) { // Select Success
          for (int i = 0; i < int(LEN) - 3; i++) {      
          while (Serial1.available() == 0) ;
          byte c = Serial1.read();
          storedata[i] = c;
          }  
          }
          
      while (Serial1.available() == 0) ;    
          CHKSUM = Serial1.read();
      if (STATUS == 0x00){ // operation ok
            Serial1.flush();
            return 0;
            }
      else{
            return 1;
      }
       }

  void array_to_string(byte array[], unsigned int len, char buffer[])
{
    for (unsigned int i = 0; i < len; i++)
    {
        byte nib1 = (array[i] >> 4) & 0x0F;
        byte nib2 = (array[i] >> 0) & 0x0F;
        buffer[i*2+0] = nib1  < 0xA ? '0' + nib1  : 'A' + nib1  - 0xA;
        buffer[i*2+1] = nib2  < 0xA ? '0' + nib2  : 'A' + nib2  - 0xA;
    }
    buffer[len*2] = '\0';
}



  String convert_tostr(byte data){
   switch(data){
    case 0x55 : return "U"; 
    case 0x45 : return "E";
    case 0x46 : return "F";
    case 0x43 : return "C";
    case 0x47 : return "G";
    case 0x52 : return "R";
    case 0x4c : return "L";
    case 0x53 : return "S"; 
    case 0x50 : return "P";
    case 0x04 : return "04";
    case 0x00 : return "00";
    case 0x03 : return "03";
    case 0x01 : return "01";
    case 0x02 : return "02";
    case 0x05 : return "05";
    case 0x06 : return "06";
    case 0x07 : return "07";
    case 0x09 : return "09";
    case 0x99 : return "99";
    default: return String(data);
   }
   }

   byte str_tohex(String str){
    return (str,HEX);
   }

  String section = "";
  bool card_OK = false;
  bool find_status = false;
  String  prevRFID = "";
  int len_i = 0;
  int repeat = 0;
  unsigned long rfid_mill = 140;
  int try_read = 0;
  bool RFID_CHECK(byte startblock,byte number){
       try_read ++;
        rfidbuffer = "";
        byte storedata[16];
        unsigned long cur = millis();
        if(RFID_login() == LOGIN_SUCCEED){
        if(readBlock(startblock,number,storedata)==0){
        card_OK = true;
        for(int i=0;i<8;i++){
        rfidbuffer += convert_tostr(storedata[i]);
        }
        }else{
        }
        }
        for(int i=0;i<15;i++){
          Serial.print(storedata[i]);
        }
        }


           




