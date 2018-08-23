#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import paho.mqtt.client as paho
import time
import uuid
import Queue
import subprocess
import unicodedata

from Config import Functions as mf

messages = Queue.Queue()
currentModule = ''

def mqtt_on_message( client, userdata, message ):
    global messages

    try:
        messages.put_nowait( message )
    except:
        raise


def mqtt_on_connect( client, arg1, arg2, arg3 ):
    global mf

    client.subscribe( mf.CONTROL_TOPIC )
    print( '[Mayordomo] Esperando en %s - %s' % ( mf.MQTT_SERVER, mf.CONTROL_TOPIC ) )


def main():
    global mf, messages, currentModule

    print( '[Mayordomo] Iniciando...' )
    mySubprocess = [
        subprocess.Popen( ['/bin/sh', './Speak.sh'], shell=False ),
        subprocess.Popen( ['/bin/sh', './Sound.sh'], shell=False ),
        subprocess.Popen( ['/usr/bin/python', './MusicPlayer/MusicPlayer.py'], shell=False )
    ]

    mqtt_client = paho.Client( 'Mayordomo-' + uuid.uuid4().hex )
    mqtt_client.on_connect = mqtt_on_connect
    mqtt_client.on_message = mqtt_on_message
    while( True ):
        try:
            mqtt_client.connect( mf.MQTT_SERVER, mf.MQTT_PORT )
            break
        except Exception as e:
            print( '[Mayordomo] Servidor MQTT %s: %s' % ( mf.MQTT_SERVER, e ) )
            time.sleep( 1 )
    mqtt_client.loop_start()

    time.sleep( 2 )
    mf.sendToSound( mqtt_client, 'Sounds/Running.ogg' );
    print( '[Mayordomo] Iniciado' )

    abort = False
    while( not abort ):
        # hacemos el manejo del payload que viene en utf-8 (se supone)
        # la idea es cambiar tildes y otros caracteres especiales
        # y llevar todo a minuscula
        message = messages.get()
        cmdLine = message.payload.decode( 'utf-8' ).lower()
        cmdLine = ''.join( ( c for c in unicodedata.normalize( 'NFD', cmdLine ) if unicodedata.category( c ) != 'Mn' ) )
        cmdLine = cmdLine.strip()

        # ajustamos algunas palabras mal convertidas por el reconocimiento de voz en android
        #cmdLine = cmdLine.replace( 'mary', 'mari' )

        # el comando y los parámetros
        print( '[Mayordomo] Mensaje recibido:', cmdLine, '<<' + message.payload + '>>' )
        argv = cmdLine.split()
        if( len( argv ) == 0 ):
            continue
        cmdLine = ' '.join( argv )

        # define hacia quien van dirigidos las ordenes siguientes
        if( argv[0] == 'control' ):
            currentModule = 'control'
            mf.sendToSpeak( mqtt_client, 'Dime Padre' )
        elif( argv[0] == 'player' ):
            currentModule = argv[0]
            mf.sendToSound( mqtt_client, 'Sounds/Module.ogg' )

        # destinadas a este módulo (control)
        elif( currentModule == 'control' ):
            if( cmdLine == 'finaliza' ):
                abort = True
            elif( cmdLine == 'que hora es' ):
                now = time.localtime()
                mf.sendToSpeak( mqtt_client, 'son las %d horas con %d minutos' % (now.tm_hour, now.tm_min) )
            elif( cmdLine == 'conversemos' ):
                mf.sendToSpeak( mqtt_client, 'de que deseas conversar?' )
            else:
                mf.sendToSound( mqtt_client, 'Sounds/Error.ogg' )

        # destinados al reproductor de música
        elif( currentModule == 'player' ):
            mqtt_client.publish( mf.MPLAYER_TOPIC, cmdLine )

    # eso es todo
    mqtt_client.publish( mf.MPLAYER_TOPIC, 'exit' )
    mf.sendToSound( mqtt_client, 'Sounds/Finish.ogg' );
    time.sleep( 2 )
    mqtt_client.loop_stop()
    for p in mySubprocess:
        p.send_signal( subprocess.signal.SIGTERM )
    time.sleep( 2 )
    print( '[Mayordomo] Sistema finalizado' )

#--
main()
