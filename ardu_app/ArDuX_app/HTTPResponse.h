#ifndef __HTTP_RESPONSE_H__
#define __HTTP_RESPONSE_H__

class HTTPResponse {
  public:
    int code;
    int content_length;
    String data;  
};
#endif // __HTTP_RESPONSE_H__

