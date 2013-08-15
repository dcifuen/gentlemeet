#ifndef __DEVICE_H__
#define __DEVICE_H__

#define HTTP_CLIENT_DEFAULT_TIMEOUT         30000  // 3s

//Local Host
#define HOST "http://192.168.1.132:8080/device/"
//Production Host
//#define HOST "http://192.168.1.120:8080/_ah/api/devices/v1/device/"

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
        boolean has_resource; 
    } configuration;

  private:
 
    WiFly* wifly;
    HTTPClient http;
};

#endif // __DEVICE_H__
