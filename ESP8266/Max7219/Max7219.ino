#include <ESP8266WiFi.h>
extern "C" { 
#include "user_interface.h" 
}
#include <ArduinoJson.h>

#include <ESP8266MQTTClient.h>
MQTTClient mqtt;

#include <LEDMatrixDriver.hpp>
#define LEDMATRIX_CS_PIN    D2
#define LEDMATRIX_DIN_PIN   D7
#define LEDMATRIX_CLK_PIN   D5
#define LEDMATRIX_SEGMENTS  1

// The LEDMatrixDriver class instance
LEDMatrixDriver lmd( LEDMATRIX_SEGMENTS, LEDMATRIX_CS_PIN );

// editor en https://xantorohara.github.io/led-matrix-editor/
const byte IMAGES[][8] = {
{
  B00000000,
  B00111100,
  B01100110,
  B01101110,
  B01110110,
  B01100110,
  B01100110,
  B00111100
}
,{
  B00000000,
  B00011000,
  B00011000,
  B00111000,
  B00011000,
  B00011000,
  B00011000,
  B01111110
},{
  B00000000,
  B00111100,
  B01100110,
  B00000110,
  B00001100,
  B00110000,
  B01100000,
  B01111110
},{
  B00000000,
  B00111100,
  B01100110,
  B00000110,
  B00011100,
  B00000110,
  B01100110,
  B00111100
},{
  B00000000,
  B00001100,
  B00011100,
  B00101100,
  B01001100,
  B01111110,
  B00001100,
  B00001100
},{
  B00000000,
  B01111110,
  B01100000,
  B01111100,
  B00000110,
  B00000110,
  B01100110,
  B00111100
},{
  B00000000,
  B00111100,
  B01100110,
  B01100000,
  B01111100,
  B01100110,
  B01100110,
  B00111100
},{
  B00000000,
  B01111110,
  B01100110,
  B00001100,
  B00001100,
  B00011000,
  B00011000,
  B00011000
},{
  B00000000,
  B00111100,
  B01100110,
  B01100110,
  B00111100,
  B01100110,
  B01100110,
  B00111100
},{
  B00000000,
  B00111100,
  B01100110,
  B01100110,
  B00111110,
  B00000110,
  B01100110,
  B00111100
}};
const int IMAGES_LEN = sizeof(IMAGES)/8;

void setup() {
  Serial.begin( 115200 );
  Serial.println();
  Serial.println();

  wifi_set_phy_mode( PHY_MODE_11G );
  WiFi.mode( WIFI_STA );
  WiFi.setAutoConnect( true );
  WiFi.begin( "Tito's Demos", "santotomas" );
  WiFi.printDiag( Serial );

  lmd.setEnabled( true );
  lmd.setIntensity( 10 );
  lmd.clear();
  lmd.display();

  Serial.print( "Conectando a la WiFi: ." );
  while( WiFi.status() != WL_CONNECTED ) {
    Serial.print(".");
    delay(500);
  }
  Serial.println( " Conectado" );

  mqtt.onConnect( []() {
    Serial.println( "Conectado a servidor MQTT" );
    mqtt.subscribe( "rcr/Max7219", 0 );      // 0 = QOS0
  });

  mqtt.onData( []( String topic, String payload, bool cont ) {
    Serial.printf( "Data recibida: %s, data: %s\r\n", topic.c_str(), payload.c_str() );
    int digit = payload.toInt();
    Serial.println( digit );
    if( digit>=0 && digit<=9 ){
      drawSprite( IMAGES[digit], 0, 0, 8, 8 );
      lmd.display();
    }
  });

  mqtt.begin( "mqtt://192.168.222.100:1883" );
}

void loop() {
  mqtt.handle();
}

void drawSprite( const byte* sprite, int x, int y, int width, int height )
{
  for( int iy = 0; iy < height; iy++ )
  {
    byte mask = B10000000;
    for( int ix = 0; ix < width; ix++ )
    {
      lmd.setPixel( y + iy, x + ix, (bool)(sprite[height - iy - 1] & mask ) );
      mask = mask >> 1;
    }
  }
}

