#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import paho.mqtt.client as paho
import json
import time
import uuid
import Queue
import numpy as np
import matplotlib.pyplot as plt

MQTT_SERVER = 'localhost'
MINDSET_TOPIC  = 'rcr/MindSet'

messages = Queue.Queue( 1 )

def mqtt_on_message( client, userdata, message ):
    global messages

    # si no se ha procesado el ultimo mensaje lo eliminamos
    try:
        messages.get_nowait()
    except Queue.Empty:
        pass

    # agregamos el mensaje
    try:
        messages.put_nowait( message )
    except Queue.Full:
            pass

def mqtt_on_connect( client, arg1, arg2, arg3 ):
    global MINDSET_TOPIC, MQTT_SERVER

    client.subscribe( MINDSET_TOPIC )
    print( "[MinSetGraphics] Esperando en %s - %s" % ( MQTT_SERVER, MINDSET_TOPIC ) )

def main():
    global mqtt_client, MQTT_SERVER, messages

    print( '[MinSetGraphics] Iniciando aplicación' )
    attentionESense = [0]*64
    meditationESense = [0]*64
    rawWave16Bit = [0]*64

    fig = plt.figure( figsize=( 9, 3 ) )
    fig.subplots_adjust( wspace=0.3, hspace=0.3 )
    plt.show( block=False )

    plt.subplot( 1, 3, 1 )
    plt.ylim( 0, 101 )
    plt.grid( True )
    plt.title( "Attention ESense", { "fontsize": 8 } )
    plt.tick_params(axis='both', which='major', labelsize=8)
    liAtt, = plt.plot( attentionESense, "r.-"  )

    plt.subplot( 1, 3, 2 )
    plt.ylim( 0, 101 )
    plt.grid( True )
    plt.title( "Meditation ESense", { "fontsize": 8 } )
    plt.tick_params(axis='both', which='major', labelsize=8)
    liMed, = plt.plot( meditationESense, "b.-" )

    plt.subplot( 1, 3, 3 )
    plt.ylim( -3000, 3000 )
    plt.grid( True )
    plt.title( "Raw Wave 16Bit", { "fontsize": 8 } )
    plt.tick_params(axis='both', which='major', labelsize=8)
    liRaw, = plt.plot( rawWave16Bit, "b-" )

    mqtt_client = paho.Client( 'MindSetGraphics-' + uuid.uuid4().hex )
    mqtt_client.on_connect = mqtt_on_connect
    mqtt_client.on_message = mqtt_on_message
    mqtt_client.connect( MQTT_SERVER, 1883 )
    mqtt_client.loop_start()
    abort = False
    while( not abort ):
        try:
            liAtt.set_ydata( attentionESense )
            liMed.set_ydata( meditationESense )
            liRaw.set_ydata( rawWave16Bit )

            time.sleep( 0 )
            fig.canvas.draw()
            time.sleep( 0 )

            message = messages.get()
            if( message.payload == 'exit' ):
                abort = True
                continue
            msg = json.loads( message.payload )

            attentionESense.pop( 0 )
            attentionESense.append( msg["attentionESense"] );
            meditationESense.pop( 0 )
            meditationESense.append( msg["meditationESense"] );
            rawWave16Bit.pop( 0 )
            rawWave16Bit.append( msg["rawWave16Bit"] );

        except Exception as e:
            pass

    mqtt_client.loop_stop()
    print( '[MinSetGraphics] Aplicación finalizada' )

#--
main()

