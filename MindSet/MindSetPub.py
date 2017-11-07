#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import paho.mqtt.client as paho
import json
import time
import uuid
from rcr.mindset.MindSet import *

MQTT_SERVER = 'localhost'
SPEAK_TOPIC = 'rcr/Speak'
MINDSET_TOPIC  = 'rcr/MindSet'

def sendToSpeak( msg ):
    global mqtt_client, SPEAK_TOPIC

    mqtt_client.publish( SPEAK_TOPIC, msg )

def mqtt_on_message( client, userdata, message ):
    global abort

    #print( message.payload )
    if( message.payload == 'exit' ):
        abort = True

def mqtt_on_connect( client, arg1, arg2, arg3 ):
    global MINDSET_TOPIC, MQTT_SERVER

    client.subscribe( MINDSET_TOPIC )
    print( "[MindSet] Enviando data a %s - %s" % ( MQTT_SERVER, MINDSET_TOPIC ) )

def main():
    global mqtt_client, MINDSET_TOPIC, MQTT_SERVER, abort

    print( '[MindSet] Iniciando aplicación' )
    mqtt_client = paho.Client( 'MindSet-' + uuid.uuid4().hex )
    mqtt_client.on_connect = mqtt_on_connect
    mqtt_client.on_message = mqtt_on_message
    mqtt_client.connect( MQTT_SERVER, 1883 )
    mqtt_client.loop_start()
    mindset = MindSet( "/dev/rfcomm4" )
    if( mindset.connect() ):
        msd = MindSetData()
        sendToSpeak( 'Sensor neuronal iniciado' )
        abort = False
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
        mindset.disconnect()
    else:
        sendToSpeak( 'Sensor neuronal no encontrado' )
        print( '[MindSet] Sin conexión al sensor' )

    sendToSpeak( 'Sensor neuronal finalizado' )
    mqtt_client.loop_stop()
    print( '[MindSet] Finalizando aplicación' )

#--
main()

