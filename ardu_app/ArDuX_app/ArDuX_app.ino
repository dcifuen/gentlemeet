#include <Arduino.h>
#include "Debug.h"
#include <EEPROM.h>
#include "TimerOne.h"
#include <SoftwareSerial.h>
#include <WiFly.h>
#include "Device.h"
#include <HttpClient.h>
#include "HTTPResponse.h"
#include <aJSON.h>
#include <Wire.h>
#include "U8glib.h"
#include "TM1637.h"
#include <Adafruit_PN532.h>
#include <SPI.h>
#include <Time.h>



#define CLK 0//pins definitions for TM1637 and can be changed to other ports    
#define DIO 1

#define SCK  (42)
#define MOSI (41)
#define SS   (10)
#define MISO (40)


#define WAITING_TICKS 60 //Multiply this with 1 second to find the time
//#define  RESET_CONF_ON_START 1

#define SSID      "Apto"
#define KEY       "12138026"
// WIFLY_AUTH_OPEN / WIFLY_AUTH_WPA1 / WIFLY_AUTH_WPA1_2 / WIFLY_AUTH_WPA2_PSK
#define AUTH      WIFLY_AUTH_WPA2_PSK

boolean sync_flag = false;
boolean syncing = false;
boolean conected = false;
int timer_ticks = 0;
int8_t TimeDisp[] = {0x00,0x00,0x00,0x00};
unsigned char ClockPoint = 1;
uint32_t nfc_id = 0;
time_t time = 0;

WiFly wifly(12, 3);

Device device;

U8GLIB_SSD1306_128X64 u8g(U8G_I2C_OPT_NONE);

TM1637 tm1637(CLK,DIO);

Adafruit_PN532 nfc(SCK, MISO, MOSI, SS);



void setup()
{
  
  #ifdef DEBUG
      Serial.begin(9600);
      DBG("************ ArDuX *************\r\n");
  #endif
  
  // assign default color value
  if ( u8g.getMode() == U8G_MODE_R3G3B2 ) {
    u8g.setColorIndex(255);     // white
  }
  else if ( u8g.getMode() == U8G_MODE_GRAY2BIT ) {
    u8g.setColorIndex(3);         // max intensity
  }
  else if ( u8g.getMode() == U8G_MODE_BW ) {
    u8g.setColorIndex(1);         // pixel on
  }
  else if ( u8g.getMode() == U8G_MODE_HICOLOR ) {
    u8g.setHiColorByRGB(255,255,255);
  }
  
  tm1637.set();
  tm1637.init();
  tm1637.display(TimeDisp);
  
  nfc.begin();

  uint32_t versiondata = nfc.getFirmwareVersion();
  
  nfc.SAMConfig();
 
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
  
  wifly.enableRTC();
  time = wifly.getTime();
  setTime(time);
  
  if (strlen(device.configuration.uuid) > 0){
     DBG("Device UID " + String(device.configuration.uuid) + "\r\n");
     DBG("Device Name " + String(device.configuration.name) + "\r\n");
     DBG("Has resource? " + String(device.configuration.has_resource ? "Yes" : "No") + "\r\n");
  }
  
  
  //Init timer interrupt every second
  Timer1.initialize(1000000);
  Timer1.attachInterrupt(sync);
  
  
}
void loop()
{
  /************* NFC ************* 
  nfc_id = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A);
  if (nfc_id > 0){
    if(!nfc.writeAllMemory(nfc_id,device.nfc_tag,sizeof(device.nfc_tag)))
         DBG("Error Writing Tag \r\n");
      else
      {
         device.read_nfc = true;
         DBG("Tag Writed \r\n");
      }
  }
  */
    
  //******** SYNC ************
  if(sync_flag){
    sync_flag = false;
    syncing = true;
    time = wifly.getTime();
    if(time > 0){
      setTime(time);
    }
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
     syncing = false;
  }  
}

void draw(){
  int w = 0;
  int h = 10;
  char buffer[6];
  sprintf(buffer , "%02d:%02d" , hourFormat12(),minute());
  u8g.setFont(u8g_font_baby);
  u8g.drawStr( 0, h, "***ArDuX*** ");
  w = w + u8g.getStrWidth("***ArDuX***") + 6;
  u8g.drawStr( w, h, SSID);
  w = w + u8g.getStrWidth(SSID) + 6;
  u8g.drawStr( w, h, buffer);
  if (syncing){
    u8g.drawStr( 120, h, "@");
  }
  h += 10;  
}

void sync(){
  
  //********* GRAPHICS *************//
  u8g.firstPage();  
  do {
    draw();
  } while( u8g.nextPage() );
  
  
  
  
  
  if(ClockPoint)tm1637.point(POINT_ON);
  else tm1637.point(POINT_OFF); 
  ClockPoint = (~ClockPoint) & 0x01;
  
  if(timer_ticks >= WAITING_TICKS ){
    timer_ticks = 0;
    sync_flag = true;
  }else{
    timer_ticks++;
  } 
}

