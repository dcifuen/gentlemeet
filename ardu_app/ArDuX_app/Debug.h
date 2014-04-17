
#ifndef __DEBUG_H__
#define __DEBUG_H__

#define DEBUG

#ifdef DEBUG
#define DBG(args...)       Serial.print(args)
#else
#define DBG(message)
#endif // DEBUG

#endif // __DEBUG_H__
