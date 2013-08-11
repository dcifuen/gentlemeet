#include <EEPROM.h>
#include "EEPROMStruct.h"

boolean stringComplete = false;

struct config_t
{
    String mode;
} configuration;

void setup()
{
    Serial.begin(9600);
    configuration.mode = "";
    //EEPROM_clear();
    EEPROM_readStruct(0, configuration);
    Serial.print(configuration.mode);
}
void loop()
{
   
       while (Serial.available()) {
        // get the new byte:
        char inChar = (char)Serial.read(); 
        // add it to the inputString:
        
        // if the incoming character is a newline, set a flag
        // so the main loop can do something about it:
        if (inChar == '\n') {
          stringComplete = true;
          EEPROM_writeStruct(0, configuration);
          Serial.println(configuration.mode);
        }else{
          configuration.mode += inChar;
        }
       }
      //if (c >= 0) {
      //  configuration.mode = (char)c;
      //  EEPROM_writeStruct(0, configuration);
      //  Serial.println(configuration.mode);
      //}   
}

