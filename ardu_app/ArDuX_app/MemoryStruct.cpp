#include <EEPROM.h>
#include "MemoryStruct.h"
#define EEPROM_SIZE 4096


void EEPROM_clear()
{
  for (int i = 0; i < EEPROM_SIZE; i++)
      EEPROM.write(i, 0);
}
