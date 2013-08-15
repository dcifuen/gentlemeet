#include "Debug.h"
#include "Device.h"
#include "HTTPClient.h"
#include "HTTPResponse.h"
#include "aJSON.h"
#include "EEPROMStruct.h"

Device::Device()
{
  wifly = WiFly::getInstance();
  EEPROM_readStruct(0, configuration);
}
int Device::clear(){
  EEPROM_clear();
}
int Device::register_device(){
  String url = String(HOST) + String("register");
  char buf[100];
  HTTPResponse response;
  url.toCharArray(buf, 100);
  response = http.postResponse(buf,"device", 10000);
  if(response.code == 200){
    DBG("Data recieved OK \r\n");
    char buff[response.content_length+10];
    response.data.toCharArray(buff,response.content_length+10);
    aJsonObject* root = aJson.parse(buff);
    if (root != NULL) {
      DBG("Data parsed correctly \r\n");
      aJsonObject* uuid = aJson.getObjectItem(root,"uuid"); 
      strncpy(configuration.uuid, uuid->valuestring, 50);
      EEPROM_writeStruct(0, configuration);
      return 1;
    }
  return 0;
  }else{
     return 0; 
  }
}

int Device::sync_device(){
  String url = String(HOST) + String("sync/") + String(configuration.uuid);
  char buf[100];
  HTTPResponse response;
  url.toCharArray(buf, 100);
  response = http.getResponse(buf, 10000);
  if(response.code == 200){
    DBG("Data recieved OK \r\n");
    char buff[response.content_length+10];
    response.data.toCharArray(buff,response.content_length+10);
    aJsonObject* root = aJson.parse(buff);
    if (root != NULL) {
      DBG("Data parsed correctly \r\n");
      //****** Save Data ********//
      aJsonObject* name = aJson.getObjectItem(root,"name"); 
      strncpy(configuration.name, name->valuestring, 50);
      EEPROM_writeStruct(0, configuration);
      return 1;
    }
  return 0;
  }else{
     return 0; 
  }
}


