#ifndef __MEMORY_STRUCT_H__
#define __MEMORY_STRUCT_H__


#include <EEPROM.h>
#include <Arduino.h>  // for type definitions
#include "Debug.h"
#define EEPROM_SIZE 4096

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

void EEPROM_clear();


#endif // __MEMORY_STRUCT_H__
