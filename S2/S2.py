#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import paho.mqtt.client as paho
import json
import time
import uuid
import Queue
from rcr.robots.scribbler2.Scribbler2 import Scribbler2
from rcr.utils import Utils

MQTT_SERVER = 'localhost'
SPEAK_TOPIC = 'rcr/Speak'
S2_TOPIC  = 'rcr/S2'

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
    global S2_TOPIC, MQTT_SERVER

    client.subscribe( S2_TOPIC )
    print( "[S2] Esperando en %s - %s" % ( MQTT_SERVER, S2_TOPIC ) )

def main():
    global mqtt_client, MQTT_SERVER, messages

    print( '[S2] Iniciando aplicación' )
    mqtt_client = paho.Client( 'S2-' + uuid.uuid4().hex )
    mqtt_client.on_connect = mqtt_on_connect
    mqtt_client.on_message = mqtt_on_message
    mqtt_client.connect( MQTT_SERVER, 1883 )
    mqtt_client.loop_start()
    s2 = None
    abort = False
    try:
        s2 = Scribbler2( "/dev/rfcomm2", 9600, 500 )
        sendToSpeak( 'Control de robot S2 iniciado' )
    except Exception as e:
        sendToSpeak( '  No existe puerto de comunicaciones con el robot' )
        abort = True
    while( not abort ):
        message = messages.get()
        print( "[S2] Mensaje recibido:", message.payload )

        words = message.payload.split()
        cmd = words[0]
        if( cmd == 'exit' ):
            abort = True
        elif( cmd == 'name' ):
            sendToSpeak( 'El robot conectado es ' + s2.s2Inner.getName() )
        else:
            delay = 0
            try:
                delay = float( words[1] )
            except Exception as e:
                print( "[S2]", e )
                continue
            if( delay <= 0 ):
                continue
            elif( cmd == 'left' ):
                s2.getS2Motors().setMotors( -100, 100 )
                time.sleep( delay )
                s2.getS2Motors().setMotors( 0, 0 )
            elif( cmd == 'right' ):
                s2.getS2Motors().setMotors( 100, -100 )
                time.sleep( delay )
                s2.getS2Motors().setMotors( 0, 0 )
            elif( cmd == 'forward' ):
                s2.getS2Motors().setMotors( 100, 100 )
                time.sleep( delay )
                s2.getS2Motors().setMotors( 0, 0 )
            elif( cmd == 'backward' ):
                s2.getS2Motors().setMotors( -100, -100 )
                time.sleep( delay )
                s2.getS2Motors().setMotors( 0, 0 )

    sendToSpeak( 'Control de robot S2 finalizado' )
    mqtt_client.loop_stop()
    print( '[S2] Aplicación finalizada' )

#--
main()

