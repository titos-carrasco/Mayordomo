#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import paho.mqtt.client as paho
import json
import time
import uuid
import threading
import Queue

# El codigo del drone tomado desde https://github.com/sethyx/py-minidrone
from pyMiniDrone import minidrone
from pyMiniDrone import dronedict

MQTT_SERVER = 'localhost'
DRONE_TOPIC = 'rcr/RollerSpider'
SPEAK_TOPIC = 'rcr/Speak'

connected = False
mutex = threading.Lock()
messages = Queue.Queue( 1 )

DRONEMAC = 'E0:14:CD:17:3D:4E'

def refresh_data( t, data ):
    global connected, mutex

    print( "Refresh Data:", t, data )
    if t == 4:
        if( data == 'y' ):
            mutex.acquire()
            connected = True
            mutex.release()
            sendToSpeak( 'Drone conectado' )
        else:
            if( connected ):
                mutex.acquire()
                connected = False
                mutex.release()
                sendToSpeak( 'Drone desconectado' )

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
    global DRONE_TOPIC, MQTT_SERVER

    client.subscribe( DRONE_TOPIC )
    print( "DroneRollerSpider: esperando en %s - %s" % ( MQTT_SERVER, DRONE_TOPIC ) )

def main():
    global mqtt_client, MQTT_SERVER, messages, mutex

    drone = minidrone.MiniDrone( mac=DRONEMAC, callback=refresh_data )

    mqtt_client = paho.Client( 'DroneRollerSpider-' + uuid.uuid4().hex )
    mqtt_client.on_connect = mqtt_on_connect
    mqtt_client.on_message = mqtt_on_message
    mqtt_client.connect( MQTT_SERVER, 1883 )
    mqtt_client.loop_start()
    while( True ):
        message = messages.get()
        print( "Mensaje recibido:", message.payload )

        mutex.acquire()
        isConnected = connected
        mutex.release()

        if( message.payload == "exit" ):
            if( isConnected ):
                drone.land()
                time.sleep( 3 )
                drone.disconnect()
                drone.die()
            break

        if( not isConnected ):
            if( message.payload == 'connect' ):
                drone.connect()
        else:
            if( message.payload == 'disconnect' ):
                drone.land()
                time.sleep( 3 )
                drone.disconnect()
            elif( message.payload == 'takeoff' ):
                drone.takeoff()
            elif( message.payload == 'land' ):
                drone.land()
            elif( message.payload == 'turn_left' ):
                drone.turn_left()
            elif( message.payload == 'turn_right' ):
                drone.turn_right()
            elif( message.payload == 'move_left' ):
                drone.move_left()
            elif( message.payload == 'move_right' ):
                drone.move_right()
            elif( message.payload == 'move_fw' ):
                drone.move_fw()
            elif( message.payload == 'move_bw' ):
                drone.move_bw()
    mqtt_client.loop_stop()

#--
main()
