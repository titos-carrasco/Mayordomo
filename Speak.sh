#!/bin/sh

SERVER="localhost"
TOPIC="rcr/Speak"

echo "Speak: esperando en $SERVER - $TOPIC"
mosquitto_sub -h "$SERVER" -t "$TOPIC" | espeak -v "es-la+f5" -a 180

