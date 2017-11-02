#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import paho.mqtt.client as paho
import time
import uuid
import threading

# El codigo del drone tomado desde https://github.com/sethyx/py-minidrone
from pyMiniDrone import minidrone
from pyMiniDrone import dronedict

MQTT_SERVER = 'localhost'
DRONE_TOPIC = 'rcr/RollerSpider'
SPEAK_TOPIC = 'rcr/Speak'

DRONEMAC = 'E0:14:CD:17:3D:4E'
drone=None
connected = False
mutex = threading.Lock()

def speak( msg ):
    global mqtt_client, SPEAK_TOPIC

    mqtt_client.publish( SPEAK_TOPIC, msg )

def refresh_data( t, data ):
    global connected, mutex

    print( t, data )
    if t == 4:
        mutex.acquire()
        if( data == 'y' ):
            connected = True
            speak( "Drone conectado" )
        else:
            if( connected ):
                connected = False
                speak( "Drone desconectado" )
        mutex.release()

def mqtt_on_message( client, userdata, message ):
    global DRONEMAC, drone, connected, mutex

    print( message.payload )
    if( message.payload == 'connect' ):
        if( drone == None ):
            drone = minidrone.MiniDrone( mac=DRONEMAC, callback=refresh_data )
            drone.connect()
        else:
            speak( 'Drone conectado' )
    elif( message.payload == 'disconnect' ):
        if( drone!=None ):
            drone.disconnect()
            while( connected ):
                time.sleep( 1 )
            drone.die()
            drone = None
        else:
            speak( 'Drone desconectado' )
    elif( message.payload == 'takeoff' ):
        if( drone!=None ):
            drone.takeoff()
    elif( message.payload == 'land' ):
        if( drone!=None ):
            drone.land()

def mqtt_on_connect( client, arg1, arg2, arg3 ):
    global DRONE_TOPIC, MQTT_SERVER

    client.subscribe( DRONE_TOPIC )
    print( "DroneRollerSpider: esperando en %s - %s" % ( MQTT_SERVER, DRONE_TOPIC ) )

def main():
    global player, mqtt_client, MQTT_SERVER

    mqtt_client = paho.Client( 'DroneRollerSpider-' + uuid.uuid4().hex )
    mqtt_client.on_connect = mqtt_on_connect
    mqtt_client.on_message = mqtt_on_message
    mqtt_client.connect( MQTT_SERVER, 1883 )
    mqtt_client.loop_forever()

#--
main()
