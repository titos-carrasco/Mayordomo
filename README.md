Mayordomo
=========

Entorno de microcontroladores/software conectados a través de MQTT y controlados a través de una aplicación desarrollada en Python (**Mayordomo.py**). 

Las órdenes pueden ser enviadas desde una app en Android por comandos de voz y sus resultados pueden ser audibles

Las componentes principales corresponden a:

- **VoiceAndMQTT**: app para Android que convierte Voz a Texto y lo envía al tópico utilizado por Mayordomo; el sentido es que éstos mensajes correspondan a las ordenes a ejecutar. La app VoiceAndMqtt se encuentra en [https://github.com/titos-carrasco/VoiceAndMQTT](https://github.com/titos-carrasco/VoiceAndMQTT)

- **Speak.sh**: script shell que recibe texto en el tópico `rcr/Mayordomo/Speak` y lo envía al sistema de audio del equipo

- **Sound.sh** script shell que recibe el nombre de un archivo de sonido en el tópico `rcr/Mayordomo/Sound` y lo reproduce a través del sistema de audio del equipo
- **Mayordomo.py**: punto central de recepción de comandos recibidos en el tópico `rcr/Mayordomo`. Los comandos principales corresponden a:
    - `control`: dirige todos los comandos siguientes hacia el mayordomo los que corresponden a:
        - `que hora es` responde con lo hora del sistema
        - `finaliza` finaliza la ejecución 
    - `player`: dirige todos los comandos siguientes hacia el reproductor de música los que corresponden a:
        - `play` inicia la reproducción de la pista de audio actual
        - `pausa` pone en pausa el reproductor
        - `stop` detiene la reproducción de la pista actual
        - `siguiente` avanza hacia la siguiente pista
        - `anterior`vuelve a la pista anterior




