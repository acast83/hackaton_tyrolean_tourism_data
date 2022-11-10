# Test of plintron API

Plintron API has certain limitations for requests in order to use it we have to find out these limitations. For all tests used `get_account_details()` API call.

## 1. With cooldown

### Cooldown: 30 seconds, Number of requests: 8
```
Number of seconds between responses (including cooldown)

          0.6,  90.0,
  30.0,  30.0,  90.0,
  30.0,  30.0,  90.0
```

**Time between request and response:**
```
         0.6,  60.6,
   0.5,  0.6,  60.6,
   0.7,  0.7,  60.6
```
---
### Cooldown: 60 seconds, Number of requests: 16
```
   0.7,  60.7,  120.7,
  60.6,  60.7,  120.7,
  60.8,  60.8,  120.7,
  60.8,  60.8,  120.8,
  60.8,  60.8,  120.7,
  60.6,  60.1
---
total = 1271.8
```
**Time between request and response:**
```
   0.7,  0.7,  60.7,
   0.6,  0.7,  60.7,
   0.8,  0.8,  60.7,
   0.8,  0.8,  60.8,
   0.8,  0.8,  60.7,
   0.6,  0.1
```
**Conclusion**:  
Number of seconds that you wait between requests does not affect cooldown time from plintron side.
As we can see 30 seconds and 60 seconds wait between requests still were able to send and receive only 3 requests before cooldown.

## 2. Without cooldown
### Plain requests
**number of requests**: 8  
```
number of     seconds between
 requests     requests
        3  |  0.6,  0.6, 60.5,
        5  |  0.6,  0.6,  0.6,  0.6,  0.6
```

**number of requests**: 16  
```
number of     seconds between
 requests     requests
        3  |  0.7,  0.6,  60.6,
       13  |  0.6,  0.6,   0.5,  0.6,  0.6,  0.6,  0.6,  0.6,  0.6,  0.6,  0.6,  0.5,  0.7
```

**number of requests**: 128  
```
number of     seconds between
 requests     requests
        2  |  0.8, 60.7,
       20  |  0.6,  0.5, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.5, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 60.6,
       20  |  0.6,  0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.5, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.7, 60.6,
       20  |  0.6,  0.4, 0.6, 0.6, 0.4, 0.6, 0.6, 0.6, 0.5, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 60.7,
       21  |  0.6,  0.4, 0.6, 0.5, 0.3, 0.6, 0.7, 0.6, 0.6, 0.4, 0.5, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.4, 0.6, 60.5,
       20  |  0.6,  0.6, 0.7, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.5, 0.6, 0.6, 0.6, 0.6, 0.6, 0.7, 0.6, 0.6, 60.6,
       20  |  0.6,  0.6, 0.6, 0.6, 0.5, 0.4, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.5, 0.6, 0.6, 60.5,
        6  |  0.6,  0.6, 0.6, 0.6, 0.6, 0.0
 
note: ~12 seconds between cooldowns
```
**Conclusion**:  
Without waiting between requests plintron API allows you to send and receive around 20 requests (in a time period of 12 seconds) until cooldown from plintron side.


## Without cooldown
### Requests with `asyncio.gather()`

```
number of     seconds between
 requests     requests
       16  |  60.7             = 60 +  0.7
       32  |  60.8             = 60 +  0.8
       64  |  60.6             = 60 +  0.6
      128  |  60.8             = 60 +  0.8
     1024  |  73.1             = 60 + 13.1
```
**Conclusion**:  
It always takes 60 seconds to receive response from plintron API.
Only after sending 1024 requests we face some side effects (additional 13 seconds) from plintron side.
