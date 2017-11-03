/*
 * Arduino Nano conectado con un ESP-01 utilizando un ESP-01 Adapter
 */

#define WIFI_RX_PIN     2
#define WIFI_TX_PIN     3
#define WIFI_SSID       "SSID"
#define WIFI_CLAVE      "CLAVE"

#define DHT22_PIN       5

#define MQTT_SERVER     "test.mosquitto.org"
#define MQTT_PORT       1883
#define MQTT_CLIENTID   "ArduinoNano1234567890"
#define MQTT_TOPIC      "rcr/DHT22"

#include <WiFiEsp.h>
WiFiEspClient net;

#ifndef HAVE_HWSERIAL1
#include "SoftwareSerial.h"
SoftwareSerial Serial1( WIFI_RX_PIN, WIFI_TX_PIN ); // RX, TX
#endif

#include <ArduinoJson.h>

#include <MQTTClient.h>
MQTTClient mqtt;

#include "DHT.h"
DHT dht( DHT22_PIN, DHT22 );

void setup()
{
  Serial.begin( 115200 );
  Serial.println();
  Serial.println();

  Serial1.begin( 9600 );
  WiFi.init( &Serial1 );
  WiFi.begin( WIFI_SSID, WIFI_CLAVE );

  dht.begin();

  Serial.print( "Conectando a la WiFi: ." );
  while( WiFi.status() != WL_CONNECTED ) {
    Serial.print(".");
    delay(500);
  }
  Serial.println( " Conectado" );

  mqtt.begin( MQTT_SERVER, MQTT_PORT, net );
}

void loop() {
  float dhtTemperatura = dht.readTemperature();
  float dhtHumedad = dht.readHumidity();
  if( isnan( dhtTemperatura ) || isnan( dhtHumedad ) ){
    Serial.println( "Se obtuvo NAN" );
    delay( 100 );
  }

  // en formato JSON
  StaticJsonBuffer<300> jsonBuffer;
  JsonObject& json = jsonBuffer.createObject();

  json["temperatura"] = dhtTemperatura;
  json["humedad"] = dhtHumedad;
  yield();

  json.printTo( Serial );
  Serial.println();
  yield();

  while( !mqtt.connect( MQTT_CLIENTID ) ){
    delay( 1000 );
  }

  String payload;
  json.printTo( payload );
  mqtt.publish( MQTT_TOPIC, payload, 0, 0 );       // QOS0
  yield();
  mqtt.loop();
  yield();
  mqtt.disconnect();
  yield();

  // pausa
  delay( 10000 );
}

