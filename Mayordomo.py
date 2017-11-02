#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import paho.mqtt.client as paho
import time
import uuid

MQTT_SERVER = 'localhost'
MAYORDOMO_TOPIC = 'rcr/Comando'
SPEAK_TOPIC = 'rcr/Speak'
PLAYER_TOPIC  = 'rcr/MusicPlayer'
DRONE_TOPIC = 'rcr/RollerSpider'

def speak( msg ):
    global mqtt_client, SPEAK_TOPIC

    mqtt_client.publish( SPEAK_TOPIC, msg )

def musicPlayer( msg ):
    global mqtt_client, PLAYER_TOPIC

    mqtt_client.publish( PLAYER_TOPIC, msg )

def drone( msg ):
    global mqtt_client, DRONE_TOPIC

    mqtt_client.publish( DRONE_TOPIC, msg )

def mqtt_on_message( client, userdata, message ):
    print( message.payload )
    cmd = message.payload.lower()
    if( cmd == 'marí' ):
        speak( 'Dime Padre' )
    elif( cmd == 'qué hora es' ):
        now = time.localtime()
        speak( 'son las %d horas con %d minutos' % (now.tm_hour, now.tm_min) )
    elif( cmd == 'toca música' ):
        musicPlayer( 'play' )
    elif( cmd == 'deten música' ):
        musicPlayer( 'stop' )
    elif( cmd == 'pausar música' ):
        musicPlayer( 'pause' )
    elif( cmd == 'tema siguiente' ):
        musicPlayer( 'next' )
    elif( cmd == 'tema anterior' ):
        musicPlayer( 'previous' )
    elif( cmd == 'conecta spider' ):
        drone( 'connect' )
    elif( cmd == 'desconecta spider' ):
        drone( 'disconnect' )
    elif( cmd == 'subir spider' ):
        drone( 'takeoff' )
    elif( cmd == 'bajar spider' ):
        drone( 'land' )

def mqtt_on_connect( client, arg1, arg2, arg3 ):
    global MAYORDOMO_TOPIC, MQTT_SERVER

    client.subscribe( MAYORDOMO_TOPIC )
    print( "Mayordomo: esperando en %s - %s" % ( MQTT_SERVER, MAYORDOMO_TOPIC ) )

def main():
    global mqtt_client, MQTT_SERVER

    mqtt_client = paho.Client( 'Mayordomo-' + uuid.uuid4().hex )
    mqtt_client.on_connect = mqtt_on_connect
    mqtt_client.on_message = mqtt_on_message
    mqtt_client.connect( MQTT_SERVER, 1883 )
    mqtt_client.loop_forever()

#--
main()
