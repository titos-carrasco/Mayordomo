#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import paho.mqtt.client as paho
import json
import time
import uuid
from rcr.mindset.MindSet import *

MQTT_SERVER = 'localhost'
MINDSET_TOPIC  = 'rcr/MindSet'

def mqtt_on_message( client, userdata, message ):
    global abort

    #print( message.payload )
    if( message.payload == 'exit' ):
        abort = True

def mqtt_on_connect( client, arg1, arg2, arg3 ):
    global MINDSET_TOPIC, MQTT_SERVER

    client.subscribe( MINDSET_TOPIC )
    print( "MindSet: enviando data a %s - %s" % ( MQTT_SERVER, MINDSET_TOPIC ) )

def main():
    global mqtt_client, MINDSET_TOPIC, MQTT_SERVER, abort

    mindset = MindSet( "/dev/rfcomm4" )
    if( mindset.connect() ):
        abort = False
        msd = MindSetData()
        mqtt_client = paho.Client( 'MindSet-' + uuid.uuid4().hex )
        mqtt_client.on_connect = mqtt_on_connect
        mqtt_client.on_message = mqtt_on_message
        mqtt_client.connect( MQTT_SERVER, 1883 )
        mqtt_client.loop_start()
        while( not abort ):
            mindset.getMindSetData( msd )
            payload = json.dumps( {
                        "poorSignalQuality": msd.poorSignalQuality,
                        "attentionESense": msd.attentionESense,
                        "meditationESense": msd.meditationESense,
                        "rawWave16Bit": msd.rawWave16Bit,
                        "when": time.time()
                      } )
            #print( payload )
            try:
                mqtt_client.publish( MINDSET_TOPIC, payload )
            except Exception as e:
                pass
            time.sleep( 0.100 )
        mqtt_client.loop_stop()
        mindset.disconnect()

#--
main()

