#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Vars import *

def sendToSpeak( mqtt_client, msg ):
    global SPEAK_TOPIC
    mqtt_client.publish( SPEAK_TOPIC, msg )

def sendToSound( mqtt_client, msg ):
    global SOUND_TOPIC
    mqtt_client.publish( SOUND_TOPIC, msg )

