#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import paho.mqtt.client as paho
import time
import uuid
import Queue
import subprocess
import dbus

import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from Config import Functions as mf

messages = Queue.Queue( 1 )

class Audacious:
    def __init__( self ):
        try:
            session= dbus.SessionBus().get_object( 'org.atheme.audacious', '/org/atheme/audacious' )
            self.audacious = dbus.Interface( session, 'org.atheme.audacious' )
        except Exception as e:
            print( e )

    def play( self ):
        try:
            self.audacious.Play()
        except Exception as e:
            print( e )

    def pause( self ):
        try:
            self.audacious.Pause()
        except Exception as e:
            print( e )

    def stop( self ):
        try:
            self.audacious.Stop()
        except Exception as e:
            print( e )

    def next( self ):
        try:
            self.audacious.Advance()
        except Exception as e:
            print( e )

    def previous( self ):
        try:
            self.audacious.Reverse()
        except Exception as e:
            print( e )


def mqtt_on_message( client, userdata, message ):
    global messages

    # si no se ha procesado el ultimo mensaje lo eliminamos
    try:
        messages.get_nowait()
    except Queue.Empty:
        pass

    # dejamos el mensaje para ser procesado
    try:
        messages.put_nowait( message )
    except Queue.Full:
        pass


def mqtt_on_connect( client, arg1, arg2, arg3 ):
    global mf

    client.subscribe( mf.MPLAYER_TOPIC )
    print( "[MusicPlayer] Esperando en %s - %s" % ( mf.MQTT_SERVER, mf.MPLAYER_TOPIC ) )


def main():
    global mf, messages

    print( '[MusicPlayer] Iniciando...' )
    mySubprocess = [
        subprocess.Popen( ['/usr/bin/audacious'], shell=False )
    ]

    time.sleep( 2 )
    player = Audacious()

    mqtt_client = paho.Client( 'MusicPlayer-' + uuid.uuid4().hex )
    mqtt_client.on_connect = mqtt_on_connect
    mqtt_client.on_message = mqtt_on_message

    while( True ):
        try:
            mqtt_client.connect( mf.MQTT_SERVER, mf.MQTT_PORT )
            break
        except Exception as e:
            print( '[MusicPlayer] Servidor MQTT %s: %s' % ( mf.MQTT_SERVER, e ) )
            time.sleep( 1 )
    mqtt_client.loop_start()

    while( True ):
        message = messages.get()
        cmdLine = message.payload
        print( "[MusicPlayer] Mensaje recibido:", cmdLine )

        if( cmdLine == 'exit' ):
            break
        elif( cmdLine == 'play' ):
            player.play()
        elif( cmdLine == 'pausa' ):
            player.pause()
        elif( cmdLine == 'stop' ):
            player.stop()
        elif( cmdLine == 'siguiente' ):
            player.next()
        elif( cmdLine == 'anterior' ):
            player.previous()
        else:
            mf.sendToSound( mqtt_client, 'Sounds/Error.ogg' )

    mqtt_client.loop_stop()
    for p in mySubprocess:
        p.send_signal( subprocess.signal.SIGTERM )
    time.sleep( 2 )
    print( '[MusicPlayer] Aplicación finalizada' )

#--
main()

