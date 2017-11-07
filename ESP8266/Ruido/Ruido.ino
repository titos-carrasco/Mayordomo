#include <ESP8266WiFi.h>
extern "C" { 
#include "user_interface.h" 
}
#include <ArduinoJson.h>

#include <ESP8266MQTTClient.h>
MQTTClient mqtt;

//#define MQTT_SERVER     "mqtt://192.168.222.100"
#define MQTT_SERVER     "mqtt://192.168.222.100:1883"
#define MQTT_CLIENTID   "NodeMCURuido1234567890"
#define MQTT_TOPIC      "rcr/Ruido"

void setup() {
  Serial.begin( 115200 );
  Serial.println();
  Serial.println();

  wifi_set_phy_mode( PHY_MODE_11G );
  WiFi.mode( WIFI_STA );
  WiFi.setAutoConnect( true );
  WiFi.begin( "Tito's Demos", "santotomas" );
  //WiFi.printDiag( Serial );

  Serial.print( "Conectando a la WiFi: ." );
  while( WiFi.status() != WL_CONNECTED ) {
    Serial.print(".");
    delay(500);
  }
  Serial.println( " Conectado" );

  mqtt.onConnect( []() {
    Serial.println( "Conectado a servidor MQTT" );
  });

  mqtt.begin( MQTT_SERVER );
}

char str[32];
void loop() {
  int noise = analogRead( A0 );
  sprintf( str, "%d", noise );
  //Serial.print( MQTT_TOPIC );
  //Serial.print( " " );
  //Serial.println( noise );
  mqtt.publish( MQTT_TOPIC, str, 0, 0 );        // QOS0
  yield();
  mqtt.handle();
  yield();
  delay( 100 );
}


