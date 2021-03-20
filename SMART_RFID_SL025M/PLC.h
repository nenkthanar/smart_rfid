#ifndef PLC_h
#define PLC_h

#include <Arduino.h>

class PLC{
private:
    Stream *_serial;
public:
    byte PLCreadData[60]; //global variable to keep readback data from PLC
    char cbuff[40];
    byte byteDummy[16];
    byte previousRFBuffer[16];

public:
    void PLCread(String adr, byte len); // length is from 0-255
    void PLCwrite(byte* data, String adr, byte len);
    byte PLCchecksum(byte * data, int len);
    bool readRFID_PLC(String addr, byte *data, byte bSize, byte numword);
    bool readAddress_PLC(String addr, byte *data, byte bSize, byte numword);
    //bool readAlarm_PLC();
    //bool readState_PLC();

    void print_byte_array(byte *buffer, byte bufferSize);
    void zero_byte_array(byte *buffer, byte bufferSize);
    String bytes2string(byte *buffer, byte idx, byte len);
    String plcword2string(byte *buffer, byte idx, byte wordcnt);
    int char2int(char c);
    void byte2plcword(byte k);
    void char2plcword(char c);

    void setSerial(Stream &streamObject);
    void sendText(char *someText);
    void begin(Stream &serial);
    bool availableSerial();
    uint8_t readByte();
    void flushSerial();
    void writeByte(uint8_t val);
    void writeByte(uint8_t val[], uint8_t len);
};

#endif

