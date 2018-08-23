#!/bin/sh

. ./Config/Vars.py

echo "[Sound] Esperando en $MQTT_SERVER - $SOUND_TOPIC"

trap 'pkill -P $!' TERM
( mosquitto_sub -h "$MQTT_SERVER" -t "$SOUND_TOPIC" | xargs -0 -d'\n' -L1 ogg123 > /dev/null 2>&1 ) & wait

