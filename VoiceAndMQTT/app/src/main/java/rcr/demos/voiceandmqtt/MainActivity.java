package rcr.demos.voiceandmqtt;

import java.util.ArrayList;
import java.util.UUID;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.speech.RecognizerIntent;
import android.util.Log;
import android.view.View;
import android.content.Intent;
import android.content.ActivityNotFoundException;
import android.widget.ImageButton;
import android.widget.TextView;
import android.widget.EditText;
import android.widget.Toast;

import org.eclipse.paho.android.service.MqttAndroidClient;
import org.eclipse.paho.client.mqttv3.DisconnectedBufferOptions;
import org.eclipse.paho.client.mqttv3.IMqttActionListener;
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.IMqttMessageListener;
import org.eclipse.paho.client.mqttv3.IMqttToken;
import org.eclipse.paho.client.mqttv3.MqttCallbackExtended;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;

public class MainActivity extends AppCompatActivity {
    private ImageButton btnSpeak;
    private TextView txtHablado;
    private EditText txtServer;
    private EditText txtTopico;
    private final int REQUEST_CODE = 1963;
    private final UUID uuid = UUID.randomUUID();

    @Override
    protected void onCreate( Bundle savedInstanceState ) {
        super.onCreate( savedInstanceState );
        setContentView( R.layout.activity_main );
        txtHablado = (TextView) findViewById( R.id.txtHablado );
        txtServer = (EditText) findViewById( R.id.txtServer );
        txtTopico = (EditText) findViewById( R.id.txtTopico );
        btnSpeak = (ImageButton) findViewById( R.id.btnSpeak );
        btnSpeak.setOnClickListener( new View.OnClickListener() {
            @Override
            public void onClick( View v ) {
                btnSpeak.setEnabled( false );
                txtHablado.setText( null );
                Intent intent = new Intent( RecognizerIntent.ACTION_RECOGNIZE_SPEECH );
                intent.putExtra( RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM );
                try {
                    startActivityForResult( intent, REQUEST_CODE );
                } catch ( ActivityNotFoundException a ) {
                    Toast.makeText(getApplicationContext(), "Speech Recognizer no soportado", Toast.LENGTH_SHORT).show();
                    btnSpeak.setEnabled( true );
                }
            }
        });
    }

    @Override
    protected void onActivityResult( int requestCode, int resultCode, Intent data ) {
        super.onActivityResult( requestCode, resultCode, data );
        Log.d( "rcr/speech1", String.valueOf( requestCode ) );
        if (requestCode == REQUEST_CODE && resultCode == RESULT_OK ) {
            ArrayList<String> result = data.getStringArrayListExtra( RecognizerIntent.EXTRA_RESULTS );
            Log.d( "rcr/speech2", result.get( 0 ) );
            txtHablado.setText( result.get( 0 ) );
            publish( txtServer.getText().toString(), txtTopico.getText().toString(), result.get( 0 ) );
        }
        btnSpeak.setEnabled( true );
    }

    private void publish( final String server, final String topico, final String payload)
    {
        String clientId = "VoiceAndMQTT-" + uuid;
        Log.d( "rcr/publish", clientId );
        final MqttAndroidClient mqttAndroidClient = new MqttAndroidClient( getApplicationContext(), "tcp://" + server, clientId );
        MqttConnectOptions mqttConnectOptions = new MqttConnectOptions();
        mqttConnectOptions.setAutomaticReconnect( true) ;
        mqttConnectOptions.setCleanSession( true );

        try {
            mqttAndroidClient.connect( mqttConnectOptions, null, new IMqttActionListener() {
                @Override
                public void onSuccess( IMqttToken asyncActionToken ) {
                    Log.d( "rcr/mqtt", "Success to connect to: " + server );
                    //Toast.makeText(getApplicationContext(), "Conectado al servidor", Toast.LENGTH_SHORT).show();

                    try {
                        MqttMessage message = new MqttMessage();
                        message.setQos(0);
                        message.setPayload( payload.getBytes() );
                        mqttAndroidClient.publish(topico, message);
                        mqttAndroidClient.disconnect();
                        Toast.makeText(getApplicationContext(), "Publicado", Toast.LENGTH_SHORT).show();
                    } catch (MqttException e) {
                        Log.d("rcr/mqtt", "No se pudo enviar el mensaje");
                        Toast.makeText(getApplicationContext(), "No se pudo publicar", Toast.LENGTH_SHORT).show();
                    }

                }

                @Override
                public void onFailure( IMqttToken asyncActionToken, Throwable exception ) {
                    Log.d( "rcr/mqtt", "Failed to connect to " + server );
                    Toast.makeText(getApplicationContext(), "No se pudo conectar a servidor", Toast.LENGTH_SHORT).show();
                }
            });
        } catch ( MqttException e ){
            Toast.makeText(getApplicationContext(), "Exception", Toast.LENGTH_SHORT).show();
        }
    }
}

