#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import paho.mqtt.client as paho
import json
import time
import uuid
import dbus
import Queue

MQTT_SERVER = 'localhost'
PLAYER_TOPIC  = 'rcr/MusicPlayer'
SPEAK_TOPIC = 'rcr/Speak'

messages = Queue.Queue( 1 )

class Audacious:
    def __init__( self ):
        try:
            session= dbus.SessionBus().get_object( 'org.atheme.audacious', '/org/atheme/audacious' )
            self.audacious = dbus.Interface( session, 'org.atheme.audacious' )
        except Exception as e:
            print( e )

    def loadAndPlay( self, fname ):
        try:
            self.audacious.Stop()
            self.audacious.Clear()
            self.audacious.PlaylistAdd( fname )
            self.audacious.Play()
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

    def songTitle( self ):
        try:
            sendToSpeak( str( self.audacious.SongTitle( self.audacious.Position()) ) )
        except Exception as e:
            print( e )

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
    global PLAYER_TOPIC, MQTT_SERVER

    client.subscribe( PLAYER_TOPIC )
    print( "MusicPlayer: esperando en %s - %s" % ( MQTT_SERVER, PLAYER_TOPIC ) )

def main():
    global mqtt_client, MQTT_SERVER, messages

    player = Audacious()
    mqtt_client = paho.Client( 'MusicPlayer-' + uuid.uuid4().hex )
    mqtt_client.on_connect = mqtt_on_connect
    mqtt_client.on_message = mqtt_on_message
    mqtt_client.connect( MQTT_SERVER, 1883 )
    mqtt_client.loop_start()
    while( True ):
        message = messages.get()
        print( "Mensaje recibido:", message.payload )
        if( message.payload == 'play' ):
            player.play()
        elif( message.payload == 'pause' ):
            player.pause()
        elif( message.payload == 'stop' ):
            player.stop()
        elif( message.payload == 'next' ):
            player.next()
        elif( message.payload == 'previous' ):
            player.previous()
        elif( message.payload == 'songtitle' ):
            player.songTitle()
        elif( message.payload == 'exit' ):
            break
    mqtt_client.loop_stop()

#--
main()

