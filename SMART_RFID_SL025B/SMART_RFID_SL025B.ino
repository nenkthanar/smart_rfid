#include "SL025.h"
#include "W5500.h"
int tagState = 3;

void setup() {
 Serial.begin(115200);//For pc comunication
 Serial1.begin(115200);//UART TTL SL025M 
 Serial2.begin(115200);//rs485 connector 
 Serial3.begin(115200);//For  db9 rs232 connector
 Serial.println(" [Response]:> * Device is online RS232 * ");
 Serial2.println(" [Response]:> * Device is online RS485 * ");
 pinMode(tagState,INPUT);
 set_inet();
 ser_in[1] = '4';
}

  String serData = "";
  int cmd_count = 0;

  void autoRead(){
    if(digitalRead(tagState)==HIGH){
      ser_in[0] = '0';
      String block = String((char*)ser_in);
      int numBlock = 1;
      Serial.println(" [Response]:> block:"+ String(block.toInt()));
      RFID_Read(block.toInt(),numBlock);
      }
      }
      
  void manaulRead(){
    if(Serial.available()){
      char c = Serial.read();
    if(c != '?')ser_in[cmd_count] = c;//Skip fill data into buffer with end char
      cmd_count ++;
    if(c == '?'){
      cmd_count = 0;//Clear start count after data end with ?
    if(ser_in[0] == 'S'){
      sector = ser_in[1];
      Serial.println(" [Response]:> Sector " + String(sector));
      } 
    if(ser_in[0] == 'T'){
      Serial.println(" [Response]:> Device is online :)");
      }
    if(ser_in[0] == 'R'){
      ser_in[0] = '0';
      String block = String((char*)ser_in);
      int numBlock = 1;
      Serial.println(" [Response]:> block:"+ String(block.toInt()));
      RFID_Read(block.toInt(),numBlock);
      }
    if(ser_in[0] == 'W'){
     int num[] = {};
      num[0]=ser_in[2];
      num[1]=ser_in[3];
      String block = String((char*)num);
      Serial.println(" [Response]:> block:"+block);
    if(WriteBlock(block.toInt())==0x00){
      Serial.println(" [Response]:> Success writed :)");
      memset(ser_in, 0, sizeof(ser_in));
      }else{
      Serial.println(" [Response]:> Writed false");
      memset(ser_in, 0, sizeof(ser_in));
      }
      memset(num, 0, sizeof(num));
    }
    }
    }
    }
  void loop(){
     manaulRead();
     autoRead();
     inet_handler();
    }

   




