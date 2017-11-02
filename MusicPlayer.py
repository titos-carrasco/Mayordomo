#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import paho.mqtt.client as paho
import uuid
import dbus

MQTT_SERVER = 'localhost'
PLAYER_TOPIC  = 'rcr/MusicPlayer'
SPEAK_TOPIC = 'rcr/Speak'

class Audacious:
    def __init__( self ):
        session= dbus.SessionBus().get_object( 'org.atheme.audacious', '/org/atheme/audacious' )
        self.audacious = dbus.Interface( session, 'org.atheme.audacious' )

    def loadAndPlay( self, fname ):
        self.audacious.Stop()
        self.audacious.Clear()
        self.audacious.PlaylistAdd( tema )
        self.audacious.Play()

    def play( self ):
        self.audacious.Play()

    def pause( self ):
        self.audacious.Pause()

    def stop( self ):
        self.audacious.Stop()

    def next( self ):
        self.audacious.Advance()

    def previous( self ):
        self.audacious.Reverse()

    def songTitle( self ):
        try:
            speak( str( self.audacious.SongTitle( self.audacious.Position()) ) )
        except Exception as e:
            print( e )


def speak( msg ):
    global mqtt_client, SPEAK_TOPIC

    mqtt_client.publish( SPEAK_TOPIC, msg )

def mqtt_on_message( client, userdata, message ):
    global player

    print( message.payload )
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

def mqtt_on_connect( client, arg1, arg2, arg3 ):
    global PLAYER_TOPIC, MQTT_SERVER

    client.subscribe( PLAYER_TOPIC )
    print( "MusicPlayer: esperando en %s - %s" % ( MQTT_SERVER, PLAYER_TOPIC ) )

def main():
    global player, mqtt_client, MQTT_SERVER

    player = Audacious()
    mqtt_client = paho.Client( 'MusicPlayer-' + uuid.uuid4().hex )
    mqtt_client.on_connect = mqtt_on_connect
    mqtt_client.on_message = mqtt_on_message
    mqtt_client.connect( MQTT_SERVER, 1883 )
    mqtt_client.loop_forever()

#--
main()

