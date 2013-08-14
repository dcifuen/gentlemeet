#include "Debug.h"
#include <EEPROM.h>
#include "TimerOne.h"
#include <Arduino.h>
#include <SoftwareSerial.h>
#include <WiFly.h>
#include "Device.h"
#include <HttpClient.h>
#include "HTTPResponse.h"
#include <aJSON.h>


#define WAITING_TICKS 2 //Multiply this with 6 seconds to find the time
//#define  RESET_CONF_ON_START 1

#define SSID      "Apto"
#define KEY       "12138026"
// WIFLY_AUTH_OPEN / WIFLY_AUTH_WPA1 / WIFLY_AUTH_WPA1_2 / WIFLY_AUTH_WPA2_PSK
#define AUTH      WIFLY_AUTH_WPA2_PSK

boolean sync_flag = false;
int timer_ticks = 0;
WiFly wifly(12, 3);
Device device;


void setup()
{
  
  #ifdef DEBUG
      Serial.begin(9600);
      DBG("************ ArDuX *************\r\n");
  #endif
  #ifdef RESET_CONF_ON_START
      device.clear();
      wifly.reset(); 
  #endif
  while (1) {
    DBG("Try to join " + String(SSID)  + "\r\n");
    if (wifly.join(SSID, KEY, AUTH)) {
      DBG("Succeed joining " + String(SSID) + "\r\n");
      wifly.clear();
      break;
    } else {
      DBG("Failed to join " + String(SSID) +"\r\n");
      DBG("Wait 1 second and try again...\r\n");
      delay(1000);
    }
  }
  
  //Init timer interrupt every 8 seconds
  Timer1.initialize(8000000);
  Timer1.attachInterrupt(sync);
  
  if (strlen(device.configuration.uuid) > 0){
     DBG("Device UID " + String(device.configuration.uuid) + "\r\n");
     DBG("Device Name " + String(device.configuration.name) + "\r\n");
     DBG("Has resource? " + String(device.configuration.has_resource ? "Yes" : "No") + "\r\n");
  }
}
void loop()
{
  
  //********* SYNC *************//
  if(sync_flag){
    sync_flag = false;
    DBG("Sync in progress...\r\n");
    if(strlen(device.configuration.uuid) == 0){
        DBG("No UID found \r\n");
        if(device.register_device()){
          DBG("Device registered \r\n");
        }else{
          DBG("Error registering device \r\n");
        }
     }else{
       if(device.sync_device()){
          DBG("Device synced \r\n");
        }else{
          DBG("Error syncing device \r\n");
        }
     }
  }
}

void sync(){
  //Sync every minute
  if(timer_ticks >=2 ){
    timer_ticks = 0;
    sync_flag = true;
  }else{
    timer_ticks++;
    int wait_time = (WAITING_TICKS - timer_ticks + 1)*8;
    //DBG("Waiting for Sync " + String(wait_time) + " secs \r\n");
  } 
}

