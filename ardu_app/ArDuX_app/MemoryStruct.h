#ifndef __MEMORY_STRUCT_H__
#define __MEMORY_STRUCT_H__


#include <EEPROM.h>
#include <Arduino.h>  // for type definitions
#include "Debug.h"
#include <Adafruit_PN532.h>
#define EEPROM_SIZE 4096
#define NFCTAG_SIZE 1024

template <class T> int EEPROM_writeStruct(int ee, const T& value)
{
    const byte* p = (const byte*)(const void*)&value;
    unsigned int i;
    for (i = 0; i < sizeof(value); i++)
          EEPROM.write(ee++, *p++);
    return i;
}

template <class T> int EEPROM_readStruct(int ee, T& value)
{
    byte* p = (byte*)(void*)&value;
    unsigned int i;
    for (i = 0; i < sizeof(value); i++)
          *p++ = EEPROM.read(ee++);
    return i;
}

template <class T> int NFCTAG_writeStruct(Adafruit_PN532 nfc,  int ee, const T& value)
{
    const byte* p = (const byte*)(const void*)&value;
    int dataSize = sizeof(value);
    int blocks = dataSize/16;
    int otherBytes = dataSize % 16;
    int lastBlock = 0;
    uint8_t buff[16];
    DBG(blocks);
    DBG(otherBytes);
    unsigned int i, j;
    uint8_t success;                          
    uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 }; 
    uint8_t uidLength;                      
    uint8_t keya[6] = { 0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5 };
    uint8_t keyb[6] = { 0xD3, 0xF7, 0xD3, 0xF7, 0xD3, 0xF7 };
    success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);
    for (i = 0; i < blocks; i++){
      if(i==0){
        success = nfc.mifareclassic_AuthenticateBlock(uid, uidLength, i, 0, keya);
      }else{
        success = nfc.mifareclassic_AuthenticateBlock(uid, uidLength, i, 1, keyb);
      }
      if(!success){
        //return 0;
      }
      for (j = 0; j < 16; j++)
        buff[j] = *p++;   
      if(i==3){
        //DBG(buff);
      }
      if(!nfc.mifareclassic_WriteDataBlock(i,buff))
        return 0;
      lastBlock = i;
    }
    for (j = 0; j < otherBytes; j++)
        buff[j] = *p++;
    
    for (j = 0; j < 16-otherBytes; j++)
        buff[j] = 0x00;   
    
    nfc.mifareclassic_WriteDataBlock(++lastBlock, buff);
    return lastBlock;
}

template <class T> int NFCTAG_readStruct(Adafruit_PN532 nfc, int ee, T& value)
{
    byte* p = (byte*)(void*)&value;
    unsigned int i;
    for (i = 0; i < sizeof(value); i++)
          *p++ = nfc.mifareclassic_ReadDataBlock(ee++, *p++);
    return i;
}

void EEPROM_clear();


#endif // __MEMORY_STRUCT_H__
