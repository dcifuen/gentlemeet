#include <Arduino.h>
#include "Debug.h"
#include <EEPROM.h>
#include "TimerOne.h"
#include <SoftwareSerial.h>
#include <WiFly.h>
#include "MemoryStruct.h"
#include "Device.h"
#include <HttpClient.h>
#include "HTTPResponse.h"
#include <aJSON.h>
#include <Wire.h>
#include "U8glib.h"
#include "TM1637.h"
#include <SPI.h>
#include <Time.h>
#include "PN532_SPI.h"
#include "snep.h"
#include "NdefMessage.h"
#include <avr/wdt.h>

//#define RESET_CONF_ON_START


#define CLK 0//pins definitions for TM1637 and can be changed to other ports    
#define DIO 1

#define SCK  (42)
#define MOSI (41)
#define SS   (10)
#define MISO (40)


#define WAITING_TICKS 30 //Multiply this with 1 second to find the time
#define MAX_ERRORS 10

#define RESET_PIN 7
#define  RESET_CONF_ON_START 1

#define SSID     "MotoX"
#define KEY      "Salcedo1234"
// WIFLY_AUTH_OPEN / WIFLY_AUTH_WPA1 / WIFLY_AUTH_WPA1_2 / WIFLY_AUTH_WPA2_PSK
#define AUTH      WIFLY_AUTH_WPA2_PSK

boolean sync_flag = false;
boolean syncing = false;
boolean conected = false;
int timer_ticks = 0;
int8_t TimeDisp[] = {0x00,0x00,0x00,0x00};
unsigned char ClockPoint = 1;
uint32_t errors = 0;
time_t time = 0;

WiFly wifly(12, 3);

Device device;

U8GLIB_SSD1306_128X64 u8g(U8G_I2C_OPT_NONE);

TM1637 tm1637(CLK,DIO);

PN532_SPI pn532spi(SPI, 10);
SNEP nfc(pn532spi);
uint8_t ndefBuf[1024];



void setup()
{
  	
  digitalWrite(RESET_PIN, HIGH);
  delay(200);
  pinMode(RESET_PIN, OUTPUT); 
  
  #ifdef RESET_CONF_ON_START
      device.clear();
      
  #endif
  #ifdef DEBUG
      Serial.begin(9600);
      DBG("************ ArDuX *************\r\n");
  #endif
  
  if (strlen(device.configuration.uuid) > 0){
     DBG("Device UID " + String(device.configuration.uuid) + "\r\n");
     DBG("Device Name " + String(device.configuration.name) + "\r\n");
     DBG("Has resource? " + String(device.configuration.has_resource ? "Yes" : "No") + "\r\n");
  }
  
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
   

  char ssid[50];
  char pass[50];
  uint8_t auth = AUTH;
  
  strcpy(ssid, SSID);
  strcpy(pass, KEY);

  if(strlen(device.configuration.ssid) > 0){
    strcpy(ssid, device.configuration.ssid);
    strcpy(pass, device.configuration.pass);
    auth = device.configuration.auth;
  }else{
    strcpy(device.configuration.ssid, ssid);
    strcpy(device.configuration.pass, pass);
    device.configuration.auth = auth;
    EEPROM_writeStruct(0, device.configuration);
  }
  
  wifly.reset(); 
  
  connectWifi(ssid, pass, auth);
  
  wifly.enableRTC();
  
  updateTime();
 
  //Init timer interrupt every second
  Timer1.initialize(1000000);
  Timer1.attachInterrupt(sync);
  
}
void loop()
{  
 
  /************* NFC *************/
  if (NFCSendDeviceID()) {
    //ID sent to android, time for configuration.
    
  }   
    
  //******** SYNC ************
  if(sync_flag){
    /************** Wifi ************/
    connectWifi(device.configuration.ssid, device.configuration.pass, device.configuration.auth);
    
    sync_flag = false;
    syncing = true;
    updateTime();
    DBG("Sync in progress...\r\n");
    if(strlen(device.configuration.uuid) == 0){
        DBG("No UID found \r\n");
        if(device.register_device()){
          DBG("Device registered \r\n");
          errors = 0;
        }else{
          DBG("Error registering device \r\n");
          errors++;
        }
     }else{
       if(device.sync_device()){
          DBG("Device synced \r\n");
          errors = 0;
        }else{
          DBG("Error syncing device \r\n");
          errors++;
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
  //******** Error control ***********/
  if(errors >= MAX_ERRORS){
    DBG("Maximun errors ("+String(errors)+") reached, reboting...\r\n");
    delay(1000);
    softwareReboot();
  }
}

bool NFCSendDeviceID(){
    DBG("Send a message to Android \r\n");
    NdefMessage message = NdefMessage();
    message.addTextRecord("uuid:"+String(device.configuration.uuid));
    int messageSize = message.getEncodedSize();
    if (messageSize > sizeof(ndefBuf)) {
        DBG("ndefBuf is too small \r\n");
    }

    message.encode(ndefBuf);
    if (0 >= nfc.write(ndefBuf, messageSize, 1000)) {
        DBG("Failed \r\n");
        return false;
    } else {
        DBG("Success \r\n");
        return true;
    }

}

void connectWifi(char* ssid,char* pass, uint8_t auth){
  
  while (!wifly.isAssociated()) {
    DBG("Try to join " + String(ssid)  + "\r\n");
    if (wifly.join(ssid, pass, auth)) {
      DBG("Succeed joining " + String(ssid) + "\r\n");
      wifly.clear();
      errors = 0;
      break;
    } else {
      DBG("Failed to join " + String(ssid) +"\r\n");
      DBG("Wait 1 second and try again...\r\n");
      errors++;
      delay(1000);
    }
  } 
}
void updateTime(){
  time = wifly.getTime();
  DBG("Updating timestamp to "+ String(time)+" \r\n");
  setTime(time);
}

void softwareReboot()
{
  digitalWrite(RESET_PIN, LOW);
  while(1)
  {
  }
}



