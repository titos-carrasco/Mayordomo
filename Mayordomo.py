#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import paho.mqtt.client as paho
import json
import time
import uuid
import Queue
import subprocess
import unicodedata

MQTT_SERVER = 'localhost'
MAYORDOMO_TOPIC = 'rcr/Mayordomo'
SPEAK_TOPIC = 'rcr/Speak'
PLAYER_TOPIC  = 'rcr/MusicPlayer'
DRONE_TOPIC = 'rcr/RollerSpider'
DHT22_TOPIC = 'rcr/DHT22'
MINDSET_TOPIC  = 'rcr/MindSet'
MAX7219_TOPIC = 'rcr/Max7219'

messages = Queue.Queue( 1 )
data_dht22 = None

def sendToSpeak( msg ):
    global mqtt_client, SPEAK_TOPIC

    mqtt_client.publish( SPEAK_TOPIC, msg )

def sendToMusicPlayer( msg ):
    global mqtt_client, PLAYER_TOPIC

    mqtt_client.publish( PLAYER_TOPIC, msg )

def sendToDrone( msg ):
    global mqtt_client, DRONE_TOPIC

    mqtt_client.publish( DRONE_TOPIC, msg )

def sendToMindSet( msg ):
    global mqtt_client, MINDSET_TOPIC

    mqtt_client.publish( MINDSET_TOPIC, msg )

def sendToMax7219( msg ):
    global mqtt_client, MAX7219_TOPIC

    mqtt_client.publish( MAX7219_TOPIC, msg )

def mqtt_on_message( client, userdata, message ):
    global messages, data_dht22

    # es el dht22
    if( message.topic == DHT22_TOPIC ):
        data_dht22 = message.payload
        return

    # lon comandos para el mayordomo
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
    global MAYORDOMO_TOPIC, MQTT_SERVER

    client.subscribe( MAYORDOMO_TOPIC )
    client.subscribe( DHT22_TOPIC )
    print( "Mayordomo: esperando en %s - %s" % ( MQTT_SERVER, MAYORDOMO_TOPIC ) )

def main():
    global mqtt_client, MQTT_SERVER, messages, data_dht22

    mqtt_client = paho.Client( 'Mayordomo-' + uuid.uuid4().hex )
    mqtt_client.on_connect = mqtt_on_connect
    mqtt_client.on_message = mqtt_on_message
    mqtt_client.connect( MQTT_SERVER, 1883 )
    mqtt_client.loop_start()
    while( True ):
        message = messages.get()

        # hacemos el manejo del payload que viene en utf-8 (se supone)
        # la idea es cambiar tildes y otros caracteres especiales
        # y llevar todo a minuscula
        cmd = message.payload.decode('utf-8').lower()
        cmd = ''.join((c for c in unicodedata.normalize('NFD', cmd) if unicodedata.category(c) != 'Mn'))
        print( "Mensaje recibido:", message.payload, "=>", cmd )

        # locales
        if( cmd == 'mari' ):
            sendToSpeak( 'Dime Padre' )
        elif( cmd == 'que hora es' ):
            now = time.localtime()
            sendToSpeak( 'son las %d horas con %d minutos' % (now.tm_hour, now.tm_min) )

        # MusicPlayer
        elif( cmd == 'toca musica' ):
            sendToMusicPlayer( 'play' )
        elif( cmd == 'deten musica' ):
            sendToMusicPlayer( 'stop' )
        elif( cmd == 'pausar musica' ):
            sendToMusicPlayer( 'pause' )
        elif( cmd == 'tema siguiente' ):
            sendToMusicPlayer( 'next' )
        elif( cmd == 'tema anterior' ):
            sendToMusicPlayer( 'previous' )
        elif( cmd == 'quien canta' ):
            sendToMusicPlayer( 'songtitle' )

        # DroneRollerSpider
        elif( cmd == 'conectar spider' ):
            sendToDrone( 'connect' )
        elif( cmd == 'desconectar spider' or cmd =='desconectar spyder' ):
            sendToDrone( 'disconnect' )
        elif( cmd == 'subir spider' ):
            sendToDrone( 'takeoff' )
        elif( cmd == 'bajar spider' ):
            sendToDrone( 'land' )
        elif( cmd == 'girar spider' ):
            for i in range( 10 ):
                sendToDrone( 'turn_left' )
                time.sleep( 0.100 )

        # MindSet
        elif( cmd == 'ejecuta mindset' ):
            subprocess.Popen( '/usr/bin/python ./MindSet/MindSetPub.py', shell=True )
            subprocess.Popen( '/usr/bin/python ./MindSet/MindSetGraphics.py', shell=True )
            subprocess.Popen( '/usr/bin/python ./MindSet/MindSetMusic.py', shell=True )
        elif( cmd == 'finaliza mindset' ):
            sendToMindSet( 'exit' )

        # DHT22
        elif( cmd == 'temperatura y humedad' ):
            if( data_dht22 == None ):
                sendToSpeak( 'No tengo datos de temperatura y humedad' )
            else:
                d = data_dht22
                d = json.loads( d )
                sendToSpeak( 'La Temperatura es de %3.1f grados y la humedad es de un %3.1f por ciento' % ( d["temperatura"], d["humedad"] ) )

        # Max72129
        elif( message.payload.startswith( 'muestra ' )  and len( message.payload ) == 9 ):
            try:
                digit = int( message.payload[8] )
                sendToSpeak( "Mostrando un %d en la matriz" % digit )
                sendToMax7219( str( digit ) )
            except Exception as e:
                pass

        # salida
        elif( message.payload == 'exit' ):
            sendToMindSet( 'exit' )
            break
    mqtt_client.loop_stop()

#--
main()
