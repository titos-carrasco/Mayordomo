#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import paho.mqtt.client as paho
import json
import time
import uuid
import Queue
import rtmidi
import random

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
    print( "[MindSetMusic] Esperando en %s - %s" % ( MQTT_SERVER, MINDSET_TOPIC ) )

def main():
    global mqtt_client, MQTT_SERVER, messages

    print( '[MindSetMusic] Iniciando aplicación' )
    midiOut = rtmidi.MidiOut()
    midiOut.open_virtual_port("MindSetMusic Port")

    mqtt_client = paho.Client( 'MindSetMusic-' + uuid.uuid4().hex )
    mqtt_client.on_connect = mqtt_on_connect
    mqtt_client.on_message = mqtt_on_message
    mqtt_client.connect( MQTT_SERVER, 1883 )
    mqtt_client.loop_start()
    abort = False
    while( not abort ):
        try:
            message = messages.get()
            if( message.payload == 'exit' ):
                abort = True
                continue
            msg = json.loads( message.payload )
            nota1 = msg["attentionESense"]*127.0/100.0
            nota2 = msg["meditationESense"]*127.0/100.0
            #print( "MindSetMusic Notes:", nota1, nota2 )
            midiOut.send_message( [ 0x90, nota1, 127 ] )  # on channel 0, nota, velocidad
            midiOut.send_message( [ 0x91, nota2, 127 ] )  # on channel 1, nota, velocidad
            time.sleep( 0.5 + random.random()*2 )
            midiOut.send_message( [ 0x80, nota1, 16 ] )  # off channel 0, nota, velocidad
            midiOut.send_message( [ 0x81, nota2, 16 ] )  # off channel 1, nota, velocidad

        except Exception as e:
            print( e )

    mqtt_client.loop_stop()
    print( '[MindSetMusic] Aplicación finalizada' )

#--
main()

