

#ifndef __HTTP_CLIENT_H__
#define __HTTP_CLIENT_H__

#define HTTP_CLIENT_DEFAULT_TIMEOUT         30000  // 3s

#define HTTP_MAX_HOST_LEN                   40
#define HTTP_MAX_PATH_LEN                   128
#define HTTP_MAX_BUF_LEN                    200

#define HTTP_DEFAULT_PORT                   80

#include <Arduino.h>
#include <WiFly.h>
#include "HTTPResponse.h"

class HTTPClient {
  public:
    HTTPClient();
    int get(const char *url, int timeout = HTTP_CLIENT_DEFAULT_TIMEOUT);
    HTTPResponse getResponse(const char *url, int timeout = HTTP_CLIENT_DEFAULT_TIMEOUT);
    int get(const char *url, const char *header, int timeout = HTTP_CLIENT_DEFAULT_TIMEOUT);
    HTTPResponse getResponse(const char *url, const char *header, int timeout = HTTP_CLIENT_DEFAULT_TIMEOUT);
    int post(const char *url, const char *data, int timeout = HTTP_CLIENT_DEFAULT_TIMEOUT);
    HTTPResponse postResponse(const char *url, const char *data, int timeout = HTTP_CLIENT_DEFAULT_TIMEOUT);
    int post(const char *url, const char *headers, const char *data, int timeout = HTTP_CLIENT_DEFAULT_TIMEOUT);
    HTTPResponse postResponse(const char *url, const char *headers, const char *data, int timeout = HTTP_CLIENT_DEFAULT_TIMEOUT);
    HTTPResponse parseResponse(String raw_data);
  private:
    int parseURL(const char *url, char *host, int max_host_len, uint16_t *port, char *path, int max_path_len);
    int connect(const char *url, const char *method, const char *data, int timeout = HTTP_CLIENT_DEFAULT_TIMEOUT);
    int connect(const char *url, const char *method, const char *header, const char *data, int timeout = HTTP_CLIENT_DEFAULT_TIMEOUT);
    char get_char;

    WiFly* wifly;
};

#endif // __HTTP_CLIENT_H__

