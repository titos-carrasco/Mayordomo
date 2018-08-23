#!/bin/sh

# Descargar mbrola y la voz Venezuelan Spanish (vz1) desde http://www.tcts.fpms.ac.be/synthesis/mbrola/mbrcopybin.html
# Copiar mbrola a /usr/local/bin
# Copiar la voz vz1 a /usr/share/mbrola/vz1

. ./Config/Vars.py

echo "[Speak] Esperando en $MQTT_SERVER - $SPEAK_TOPIC"

trap 'pkill -P $!' TERM
( mosquitto_sub -h "$MQTT_SERVER" -t "$SPEAK_TOPIC" | espeak -v mb/mb-vz1 -a 150 -s 160 -p 30 -g 0 -b 1 > /dev/null 2>&1 ) & wait
