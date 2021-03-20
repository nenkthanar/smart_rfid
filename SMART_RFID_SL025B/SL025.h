 #define SEND_HEADER 0xBA
 #define OPERATION_OK 0x00
 #define NO_TAG 0x01
 #define READ_FAIL 0x04
 #define WRITE_FAIL 0x05

 #define LOGIN_SUCCEED 0x02
 #define LOGIN_FAIL 0x03
 unsigned char flag_read=0,pv_flag_read=1;
 byte rfidBuffer[16] = {};
 char sector = 'B';
 //--------------- RFID Card Reader ---------------------
 #define   CHK_BYTE1    0x04
 #define   CHK_BYTE2    0x99
 #define   IDX_CHK_BYTE1   1
 #define   IDX_CHK_BYTE2   15 

  //--------------- XBee network Communication -----------
  byte HEADER,LEN,CMD,STATUS,UID[8],TYPE,CHKSUM,BOX,AFI,DSFID;
  bool read_state =  false;
  String rfidbuffer = "";
  byte ser_in[20];
  
 byte checksum(byte (*values),int length){
   byte result = values[0];
   for (int i = 1; i < length; i++)
   result ^= values[i];
   return result;
 }
 
  byte LoginSectorA[]= {0xBA,0x0A,0x02,0x00,0xAA,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,checksum(LoginSectorA,11)};  
  byte LoginSectorB[]= {0xBA,0x0A,0x02,0x01,0xAA,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,checksum(LoginSectorB,11)};  

  
  byte RFID_login(char sector){
     if(sector == 'A'){
     Serial3.write(LoginSectorA,sizeof(LoginSectorA));
     }else{
     Serial3.write(LoginSectorB,sizeof(LoginSectorB));
     }
     while(1){
      int c = Serial3.read();
      if (c == 0xBD) break;
      }
      while (Serial3.available()==0);    
      LEN = Serial3.read();
      while (Serial3.available()==0);   
      CMD = Serial3.read();
      while (Serial3.available()==0) ;   
      STATUS = Serial3.read();
      return STATUS;
      }
     
int readBlock(int startblock,byte storedata[16]){
        byte *frame;
        frame = (byte *) malloc(5 * sizeof(byte));
        frame[0] = 0xBA;
        frame[1] = 3;
        frame[2] = 0x03;
        frame[3] = startblock;
        frame[4] = checksum(frame, 4); 
         Serial3.write(frame, 5);
        free(frame);
        frame = NULL;
      while (1){    
      while (Serial3.available()==0); 
      if(Serial3.read() == 0xBD) break;
         }     
      while (Serial3.available()==0);    
         LEN = Serial3.read();
      while (Serial3.available()==0);   
         CMD = Serial3.read();
      while (Serial3.available()==0) ;   
         STATUS = Serial3.read();
      if (STATUS == 0x00) { // Select Success
          for (int i = 0; i < int(LEN) - 3; i++) {      
          while (Serial3.available() == 0) ;
          byte c = Serial3.read();
          storedata[i] = c;
          }  
          }
          
      while (Serial3.available() == 0) ;    
          CHKSUM = Serial3.read();
      if (STATUS == 0x00){ // operation ok
            Serial3.flush();
            return 0;
            }
      else{
            return 1;
        }
       }


   bool RFID_Read(int startblock,int number){
     byte storedata[16];
        unsigned long cur = millis();
        if(RFID_login(sector) == LOGIN_SUCCEED){
        if(readBlock(startblock,storedata)==0){
        String newrfid = String((char*)storedata);
        if(rfidbuffer != newrfid){
        rfidbuffer = newrfid;//Convert byte to ascii
        Serial2.println(rfidbuffer);//Send data throught rs 485 connector
        }
        Serial.println(" [Response]:> Success reading");
        }else{
        Serial.println(" [Response]:> Reading false!!");
        }
        Serial.print(" [Data]:>");
        Serial.println(rfidbuffer);
        }else{
        Serial.println(" [Response]:> Login false !");
        }
        }

    byte WriteBlock(byte block){
      if(RFID_login(sector) == LOGIN_SUCCEED){
      byte datToWrite[]={0xBA,19,0x04,block,ser_in[3],
                         ser_in[4],ser_in[5],ser_in[6],
                         ser_in[7],ser_in[8],ser_in[9],
                         ser_in[10],ser_in[11],ser_in[12],
                         ser_in[13],ser_in[14],ser_in[15],
                         ser_in[16],ser_in[17],ser_in[18],
                         checksum(datToWrite,20)};
                         
      Serial3.write(datToWrite,sizeof(datToWrite));
      while (1){    
      while (Serial3.available()==0); 
       if(Serial3.read() == 0xBD) break;
      }
      while (Serial3.available()==0);    
       LEN = Serial3.read();
       while (Serial3.available()==0);   
       CMD = Serial3.read();
       while (Serial3.available()==0) ;   
       STATUS = Serial3.read();
      return STATUS;
      }
     }




 
