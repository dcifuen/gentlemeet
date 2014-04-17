#ifndef __DEVICE_H__
#define __DEVICE_H__

#define HTTP_CLIENT_DEFAULT_TIMEOUT  60000  // 60s

//Production Host
#define HOST "http://www-ardux.appspot.com/device/"
//Local Host
//#define HOST "http://192.168.1.121:8080/device/"

#include <Arduino.h>
#include <WiFly.h>
#include "HTTPClient.h"
#include <string.h>


class Device {
  public:
    Device();
    int register_device();
    int sync_device();
    int clear();
    struct config_t
    {
        char uuid[50];
        char name[50];
        char ssid[50];
        char pass[50];
        uint8_t auth;
        boolean has_resource;
        
    } configuration;
    
    
  private:
 
    WiFly* wifly;
    HTTPClient http;
};

#endif // __DEVICE_H__
