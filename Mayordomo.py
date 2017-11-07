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
NOISE_TOPIC = 'rcr/Ruido'
S2_TOPIC  = 'rcr/S2'

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

def sendToNoise( msg ):
    global mqtt_client, NOISE_TOPIC

    mqtt_client.publish( NOISE_TOPIC, msg )

def sendToS2( msg ):
    global mqtt_client,S2_TOPIC

    mqtt_client.publish( S2_TOPIC, msg )

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
    print( "[Mayordomo] Esperando en %s - %s" % ( MQTT_SERVER, MAYORDOMO_TOPIC ) )

def main():
    global mqtt_client, MQTT_SERVER, messages, data_dht22

    print( '[Mayordomo] Iniciando sistema' )
    subprocess.Popen( '/bin/sh ./Speak.sh', shell=True )
    subprocess.Popen( '/usr/bin/python ./MusicPlayer/MusicPlayer.py', shell=True )

    mqtt_client = paho.Client( 'Mayordomo-' + uuid.uuid4().hex )
    mqtt_client.on_connect = mqtt_on_connect
    mqtt_client.on_message = mqtt_on_message
    mqtt_client.connect( MQTT_SERVER, 1883 )
    mqtt_client.loop_start()
    time.sleep( 2 )
    sendToSpeak( '     ' )
    sendToSpeak( '    Sistema inicializado' )
    abort = False
    while( not abort ):
        message = messages.get()

        # hacemos el manejo del payload que viene en utf-8 (se supone)
        # la idea es cambiar tildes y otros caracteres especiales
        # y llevar todo a minuscula
        cmd = message.payload.decode('utf-8').lower()
        cmd = ''.join((c for c in unicodedata.normalize('NFD', cmd) if unicodedata.category(c) != 'Mn'))
        cmd = cmd.replace( 'mary', 'mari' )
        cmd = cmd.replace( 'detener', 'deten' )
        cmd = cmd.replace( 'tocar', 'toca' )
        cmd = cmd.replace( 'pausar', 'pausa' )
        cmd = cmd.replace( 'iniciar', 'inicia' )
        cmd = cmd.replace( 'finalizar', 'finaliza' )
        cmd = cmd.replace( 'mostrar', 'muestra' )
        cmd = cmd.replace( 'robots', 'robot' )
        cmd = cmd.replace( 'conectar', 'conecta' )
        cmd = cmd.replace( 'desconectar', 'desconecta' )
        print( "[Mayordomo] Mensaje recibido:", message.payload, "<<" + cmd + ">>" )

        # locales
        if( cmd == 'finaliza sistema' ):
            abort = True
        elif( cmd == 'mari' ):
            sendToSpeak( 'Dime Padre' )
        elif( cmd == 'que hora es' ):
            now = time.localtime()
            sendToSpeak( 'son las %d horas con %d minutos' % (now.tm_hour, now.tm_min) )
        elif( cmd == 'conversemos' ):
            now = time.localtime()
            sendToSpeak( 'de que deseas conversar?' )

        # MusicPlayer
        elif( cmd == 'toca musica' ):
            sendToMusicPlayer( 'play' )
        elif( cmd == 'deten musica' ):
            sendToMusicPlayer( 'stop' )
        elif( cmd == 'pausa musica' ):
            sendToMusicPlayer( 'pause' )
        elif( cmd == 'tema siguiente' ):
            sendToMusicPlayer( 'next' )
        elif( cmd == 'tema anterior' ):
            sendToMusicPlayer( 'previous' )
        elif( cmd == 'quien canta' ):
            sendToMusicPlayer( 'songtitle' )

        # DroneRollerSpider
        elif( cmd == 'inicia spider' ):
            subprocess.Popen( '/usr/bin/python ./DroneRollerSpider/DroneRollerSpider.py', shell=True )
        elif( cmd == 'finaliza spider' ):
            sendToDrone( 'exit' )
        elif( cmd == 'conecta spider' ):
            sendToDrone( 'connect' )
        elif( cmd == 'desconecta spider' or cmd =='desconectar spyder' ):
            sendToDrone( 'disconnect' )
        elif( cmd == 'sube spider' ):
            sendToDrone( 'takeoff' )
        elif( cmd == 'baja spider' ):
            sendToDrone( 'land' )
        elif( cmd == 'gira spider' ):
            for i in range( 10 ):
                sendToDrone( 'turn_left' )
                time.sleep( 0.100 )

        # MindSet
        elif( cmd == 'inicia sensor neuronal' ):
            subprocess.Popen( '/usr/bin/python ./MindSet/MindSetPub.py', shell=True )
            subprocess.Popen( '/usr/bin/python ./MindSet/MindSetGraphics.py', shell=True )
            subprocess.Popen( '/usr/bin/python ./MindSet/MindSetMusic.py', shell=True )
        elif( cmd == 'finaliza sensor neuronal' ):
            sendToMindSet( 'exit' )

        # DHT22
        elif( cmd == 'temperatura' ):
            if( data_dht22 == None ):
                sendToSpeak( 'No tengo datos de temperatura' )
            else:
                d = data_dht22
                d = json.loads( d )
                sendToSpeak( 'La Temperatura es de %3.1f grados' % ( d["temperatura"] ) )
        elif( cmd == 'humedad' ):
            if( data_dht22 == None ):
                sendToSpeak( 'No tengo datos de humedad' )
            else:
                d = data_dht22
                d = json.loads( d )
                sendToSpeak( 'La humedad es de un %3.1f por ciento' % ( d["humedad"] ) )

        # Max72129
        elif( cmd.startswith( 'muestra ' )  and len( cmd ) == 9 ):
            try:
                digit = int( cmd[8] )
                sendToSpeak( "Mostrando un %d en la matriz" % digit )
                sendToMax7219( str( digit ) )
            except Exception as e:
                pass

        # Sensor de ruido
        elif( cmd == 'inicia analisis de ruido' ):
            subprocess.Popen( '/usr/bin/python ./Noise/NoiseGraphics.py', shell=True )
        elif( cmd == 'finaliza analisis de ruido' ):
            sendToNoise( 'exit' )

        # robot S2
        elif( cmd == 'inicia control de robot' ):
            subprocess.Popen( '/usr/bin/python ./S2/S2.py', shell=True )
        elif( cmd == 'nombre de robot' ):
            sendToS2( 'name' )
        elif( cmd == 'robot izquierda' ):
            sendToS2( 'left 1' )
        elif( cmd == 'robot derecha' ):
            sendToS2( 'right 1' )
        elif( cmd == 'robot avanza' ):
            sendToS2( 'forward 5' )
        elif( cmd == 'robot retrocede' ):
            sendToS2( 'backward 5' )
        elif( cmd == 'finaliza control de robot' ):
            sendToS2( 'exit' )

    sendToSpeak( 'Sistema finalizado' )
    time.sleep( 2 )
    mqtt_client.loop_stop()
    print( '[Mayordomo] Sistema finalizado' )

#--
main()
