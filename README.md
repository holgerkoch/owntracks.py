# owntracks.py
python based owntracks client for raspberry pi


Howto:
- apt-get install gpsd gpsd-clients
- connect the gps receiver an test it, you should see a data stream
     gpspipe -r
- install the python mqtt library
     pip install paho-mqtt
- download owntracks.py and set the values
      brokerserver
      brokerport
      brokeruser, if you need authentication, if not remove the "client.username_pw_set" line
      brokerpassword, if you need authentication, if not remove the "client.username_pw_set" line
      set the clientid
      set the topic of your broker
      set max_abstand, defined in meter how often should be send a message
      max_transfer, defined in seconds, how often should be send a message
      set the ca certificate, if you use TLS encryption, otherwise remove the line "client.tls_set("ca.crt")"
- start the programm
      python owntracks.py
- you should see som output:

root@raspberrypi:~/owntracks# python owntracks.py
Connected with result code 0
5727569.43952 # distance in meter of the last send position, the first is the diffence from 0:0 
{"lat": 53.968613333, "tid": "RP", "_type": "location", "lon": 14.050865, "tst": "1457264819"}



