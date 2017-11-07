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
SPEAK_TOPIC = 'rcr/Speak'
NOISE_TOPIC  = 'rcr/Ruido'

messages = Queue.Queue( 1 )

def sendToSpeak( msg ):
    global mqtt_client, SPEAK_TOPIC

    mqtt_client.publish( SPEAK_TOPIC, msg )

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
    global NOISE_TOPIC, MQTT_SERVER

    client.subscribe( NOISE_TOPIC )
    print( "[NoiseGraphics] Esperando en %s - %s" % ( MQTT_SERVER, NOISE_TOPIC ) )

def main():
    global mqtt_client, MQTT_SERVER, messages

    print( '[NoiseGraphics] Iniciando aplicación' )
    noise = [0]*64

    fig = plt.figure( figsize=( 4, 3 ) )
    fig.subplots_adjust( wspace=0.3, hspace=0.3 )
    plt.show( block=False )

    plt.subplot( 1, 1, 1 )
    plt.ylim( 0, 1025 )
    plt.grid( True )
    plt.title( "Noise", { "fontsize": 8 } )
    plt.tick_params(axis='both', which='major', labelsize=8)
    liNoise, = plt.plot( noise, "r.-"  )

    mqtt_client = paho.Client( 'NoiseSetGraphics-' + uuid.uuid4().hex )
    mqtt_client.on_connect = mqtt_on_connect
    mqtt_client.on_message = mqtt_on_message
    mqtt_client.connect( MQTT_SERVER, 1883 )
    mqtt_client.loop_start()
    sendToSpeak( 'Analisis de ruido iniciado' )
    abort = False
    while( not abort ):
        try:
            time.sleep( 0 )
            fig.canvas.draw()
            time.sleep( 0 )

            message = messages.get()
            if( message.payload == 'exit' ):
                abort = True
                continue
            data = int( message.payload )

            noise.pop( 0 )
            noise.append( data );
            liNoise.set_ydata( noise )

        except Exception as e:
            pass

    sendToSpeak( 'Analisis de ruido finalizado' )
    mqtt_client.loop_stop()
    print( '[NoiseGraphics] Aplicación finalizada' )

#--
main()

