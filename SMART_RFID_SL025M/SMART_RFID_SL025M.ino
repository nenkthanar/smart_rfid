#include "SL025.h"

void setup() {
 Serial.begin(115200);//For pc comunication
 Serial1.begin(115200); 
 Serial2.begin(115200); 
 Serial3.begin(115200);//For  db9 rs232 connector
 Serial.println(" * Login on progress * ");
}

  String serData = "";
  void loop(){
  if(Serial3.available()){
     char c = Serial3.read();
     if(c != '?'){
     serData += c;
    }
    if(c == '?'){
      Serial3.println("[RESPONSE] => " + serData);
      serData = "";
    }
  }
  if(RFID_login()==LOGIN_SUCCEED){
   Serial.println("Login succeed 1");
   RFID_CHECK(0x04,1);
  }
  }




