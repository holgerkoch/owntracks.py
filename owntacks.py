#!/usr/bin/python
#
# owntracks.py, python basierter owntracks Client
# sendet die GPS Position per MQTT an einen Broker
#
# holgerkoch.de
#
# Version: 0.1

import os
from gps import *
import time
import datetime
import threading
import json
import paho.mqtt.client as mqtt

# wichtige Variablen definieren
# servername des Brokers
brokerserver = "<servername>"
# serverport des Brokers
brokerport = "8883"
# brokeruser, falls der Zugriff mit Username + PW abgesichert ist
brokeruser = "<username>"
# brokerpassword, falls der Zugriff mit Username + PW abgesichert ist
brokerpassword = "<password>"
# clientid, zwei Zeichen, diese erscheint dann auf der Karte
clientid = "RP"
# Topic des Brokers
topic = "owntracks/wohnmobil/" + clientid
# max_abstand, ab welcher Groesse in Meter der Positionsaenderung soll die
# aktuelle Position an den Broker gesendet werden?
max_abstand = 40
# wie haeufig, in Sekunden, soll maximal eine Position gesendet werden?
max_transfer = 5
gpsd = None

# Verbinden mit dem MQTT Broker
def on_connect(client, userdata, flags, rc):
   print("Connected with result code " + str(rc))

client = mqtt.Client(client_id=clientid)
# Kommunikation mit User + PW abgesichert, wenn nicht entfernen
client.username_pw_set(brokeruser, brokerpassword)
# ROOT CA Certificate fuer gesicherte Uebertragung, wenn nicht entfernen
client.tls_set("ca.crt")
client.on_connect = on_connect
# Host, Port und Timeout des Brokers
client.connect(brokerserver, brokerport, 60)

client.loop_start()

# Klasse um GPS zu initialisieren und kontinuierlich aus gpsd zu lesen
class GpsPoller(threading.Thread):
   def __init__(self):
      threading.Thread.__init__(self)
      global gpsd
      gpsd = gps(mode=WATCH_ENABLE)
      self.current_value = None
      self.running = True

   def run(self):
      global gpsd
      while gpsp.running:
         gpsd.next()

# hier beginnt das eigentliche Programm
if __name__ == '__main__':

   last_longitude = 0
   last_latitude = 0
   abstand = 0
   x = 0
   y = 0
   gpsp = GpsPoller() # create the thread
   try:
      gpsp.start() # start it up
      while True:
         if gpsd.utc != None and gpsd.utc != '' and gpsd.fix.latitude != 'nan' and gpsd.fix.longitude != 'nan' and gpsd.fix.latitude != '' and gpsd.fix.longitude != '':
            # abstand zur letzten gesendeten Position ermitteln
            x = 111.3 * (gpsd.fix.latitude - last_latitude)
            y = 71.5 * (gpsd.fix.longitude - last_longitude)
            # ungefaehrer Abstand in Meter
            abstand = math.sqrt(x*x + y*y)*1000
            # wenn die aktuelle Positionsaenderung groesser als max_abstand ist,
            # dann soll sie per mqtt gesendet werden
            if abstand > max_abstand:
               print abstand
               # zeitstempel ermitteln
               gpstime = datetime.datetime(int(gpsd.utc[0:4]), int(gpsd.utc[5:7]), int(gpsd.utc[8:10]), int(gpsd.utc[11:13]), int(gpsd.utc[14:16]), int(gpsd.utc[17:19]))
               timestamp = int(time.mktime(gpstime.timetuple()))
               data = {
                  '_type' : 'location',
                  'tst'   : timestamp,
                  'lat'   : gpsd.fix.latitude,
                  'lon'   : gpsd.fix.longitude,
                  'tid'   : clientid,
               }
               message = json.dumps(data)
               print message
               client.publish(topic, str(message))
               # merken der letzten gesendeten Position
               last_latitude=gpsd.fix.latitude
               last_longitude=gpsd.fix.longitude
         time.sleep(max_transfer)

   except (KeyboardInterrupt, SystemExit):
      print "\nKilling Thread..."
      # GPSD Verbindung abbauen
      gpsp.running = False
      # warten bis GPS Thread abgebaut ist
      gpsp.join()
      # MQTT Verbindung abbauen
      client.disconnect()
   print "Done.\nExiting."
