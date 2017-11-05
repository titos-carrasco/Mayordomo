#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import threading
import serial
import time

class MindSetData:
    def __init__( self ):
        self.poorSignalQuality = 200         # byte      (0 <=> 200) 0=OK; 200=sensor sin contacto con la piel - 1 x seg
        self.attentionESense = 0             # byte      (1 <=> 100) 0=no confiable - 1 x seg
        self.meditationESense = 0            # byte      (1 <=> 100) 0=no confiable - 1 x seg
        self.rawWave16Bit = 0                # int16     (-32768 <=> 32767) - 512 x seg
        self.delta = 0                       # uint32    (0 <=> 16777215) - 1 x seg
        self.theta = 0                       # uint32    (0 <=> 16777215) - 1 x seg
        self.lowAlpha = 0                    # uint32    (0 <=> 16777215) - 1 x seg
        self.highAlpha = 0                   # uint32    (0 <=> 16777215) - 1 x seg
        self.lowBeta = 0                     # uint32    (0 <=> 16777215) - 1 x seg
        self.highBeta = 0                    # uint32    (0 <=> 16777215) - 1 x seg
        self.lowGamma = 0                    # uint32    (0 <=> 16777215) - 1 x seg
        self.midGamma = 0                    # uint32    (0 <=> 16777215) - 1 x seg

class MindSet():
    def __init__( self, port ):
        self.port = port
        self.mutex = threading.Lock()
        self.connected = False

    def connect( self ):
        if( self.connected ):
            print( "MindSet Connect(): Ya se encuentra conectado a %s\n" % self.port, end='' )
            return True

        # conecta a la puerta
        print( "MindSet Connect(): Intentando conectar a %s ..." % self.port, end='' )
        try:
            self.conn = serial.Serial( self.port, baudrate=57600, bytesize=8,
                                       parity='N', stopbits=1, timeout=1 )
            self.conn.flushInput()
            self.conn.flushOutput()
            self.connected = True
        except Exception as e:
            self.conn = None
            print( "\n%s\n" % e, end='' )
            return False
        print( "OK\n", end='' )

        # inicializaciones requeridas
        self.msd = MindSetData()
        self.queue = bytearray()
        self.bytesLeidos = 0
        self.bytesPerdidos = 0
        self.paquetesProcesados = 0
        self.paquetesPerdidos = 0
        self.tRunning = False

        # levantamos la tarea de apoyo
        print( "MindSet Connect(): Levantando tarea de lectura de datos ...", end='' )
        self.tParser = threading.Thread( target=self._TParser, args=(), name="_TParser" )
        self.tParser.start()
        while ( not self.tRunning ):
            time.sleep( 0 )
        print( "OK\n", end='' )

        return True

    def disconnect( self ):
        if( self.connected ):
            # detiene tarea
            print( "MindSet Disconnect(): Deteniendo Tarea ...", end='' )
            self.tRunning = False
            self.tParser.join()
            self.tParser = None
            self.queue = None
            self.msd = None
            print( "OK\n", end='' )

            # desconecta
            print( "MindSet Disconnect(): Cerrando puerta ...", end='' )
            try:
                self.conn.close()
            except Exception as e:
                print( "\n%s\n" % e, end='' )
            self.connected = False
            self.conn = None

            print( "OK\n", end='' )
            print( "Bytes Leidos        : %d\n" % self.bytesLeidos, end='' )
            print( "Bytes Perdidos      : %d\n" % self.bytesPerdidos, end='' )
            print( "Paquetes Procesados : %d\n" % self.paquetesProcesados, end='')
            print( "Paquetes Perdidos   : %d\n" % self.paquetesPerdidos, end='' )
            print( "%s\n" % threading.enumerate(), end='' )

    def isConnected( self ):
        return self.connected

    def getMindSetData( self, msd ):
        self.mutex.acquire()
        msd.poorSignalQuality   = self.msd.poorSignalQuality
        msd.attentionESense     = self.msd.attentionESense
        msd.meditationESense    = self.msd.meditationESense
        msd.rawWave16Bit        = self.msd.rawWave16Bit
        msd.delta               = self.msd.delta
        msd.theta               = self.msd.theta
        msd.lowAlpha            = self.msd.lowAlpha
        msd.highAlpha           = self.msd.highAlpha
        msd.lowBeta             = self.msd.lowBeta
        msd.highBeta            = self.msd.highBeta
        msd.lowGamma            = self.msd.lowGamma
        msd.midGamma            = self.msd.midGamma
        self.mutex.release()

    def sendCommand( cmd ):
        # 0xC0: Connect RF Dongle with GHID [ 0xC0,  GHID_high, GHID_low ]
        # 0xC1: Disconnect RF Dongle
        # 0xC2: Connect with any RF Dongle
        # 0x00: Set 9600 baud
        # 0x01: Set 1200 baud
        # 0x02: Set 57.6k, normal + raw
        # 0x03: Set 57.6k, FFT
        # 0001 0001: Set/unset to enable/disable raw wave output
        # 0001 0010: Set/unset to use 10bit/8bit raw wave output
        # 0001 0100: Set/unset to enable/disable raw marker output
        # 0010 0001: Set/unset to enable/disable poor quality output
        # 0010 0010: Set/unset to enable/disable EEG powers (int) output
        # 0010 0100: Set/unset to enable/disable EEG powers (legacy/floats) output
        # 0010 1000: Set/unset to enable/disable battery output
        # 0011 0001: Set/unset to enable/disable attention output
        # 0011 0010: Set/unset to enable/disable meditation output
        # 0x60: no change in baud rate
        # 0x61: 1200 baud
        # 0x62: 9600 baud
        # 0x63: 57.6k baud
        try:
            self.conn.write( cmd )
        except Exception as e:
            print( "\n%s\n" % e, end='' )

    # privadas
    def _TParser( self, *args ):
        self.conn.flushInput()
        estado = 0
        plength = 0
        idx = 0
        payload = None
        self.tRunning = True
        while( self.tRunning ):
            # saca lo mas rapido posible la data del buffer serial
            try:
                if( self.conn.in_waiting > 0 ):
                    data = self.conn.read( self.conn.in_waiting )
                    if( type( data ) == str ):
                        self.queue = self.queue + bytearray( data )
                    else:
                        self.queue = self.queue + data
                    self.bytesLeidos = self.bytesLeidos + len( data )
                    if( len( self.queue ) > 512 ):
                        print( "Advertencia: bytes pendientes %d\n" % len( self.queue ), end='' )
            except Exception as e:
                #print( "%s\n" % e, end='' )
                pass

            # debe haber algo en el buffer
            if( len( self.queue ) == 0 ):
                time.sleep( 0 )
                continue

            # trabajamos con un automata
            b = self.queue.pop( 0 )

            # 0xAA 0xAA 0xAA*
            if( estado == 0 and b == 0xAA ):
                estado = 1
            elif( estado == 1 and b == 0xAA ):
                estado = 2
            elif( estado == 2 and b == 0xAA ):
                pass

            # seguido del numero de bytes de data
            elif( estado == 2 and b > 0 and b < 0xAA ):
                plength = b
                payload = bytearray( plength )
                idx = 0
                estado = 3

            # seguido de la data
            elif( estado == 3 ):
                payload[idx] = b
                idx = idx + 1
                if( idx == plength ):
                    estado = 4

            # finalmente el checksum
            elif( estado == 4 ):
                suma = 0
                for i in range( plength ):
                    suma = suma + payload[i]
                suma = ( ~( suma & 0xff ) ) & 0xff
                if( b != suma ):
                    self.bytesPerdidos = self.bytesPerdidos + 1 + plength + 1
                    self.paquetesPerdidos = self.paquetesPerdidos + 1
                    print( "_TParser(): ErrCheckSum\n", end='' )
                else:
                    self.paquetesProcesados = self.paquetesProcesados + 1
                    self._parsePayload( payload )
                estado = 0
            else:
                #print( "_TParser(): byte perdido\n", end='' )
                self.bytesPerdidos = self.bytesPerdidos + 1
                estado = 0

    def _parsePayload( self, payload ):
        pos = 0
        self.mutex.acquire()
        while pos < len( payload ):
            exCodeLevel = 0
            while( payload[pos] == 0x55 ):
                exCodeLevel = exCodeLevel + 1
                pos = pos + 1
            code = payload[pos]
            pos = pos + 1
            if( code >= 0x80 ):
                vlength = payload[pos]
                pos = pos + 1
            else:
                vlength = 1

            data = bytearray( vlength )
            for i in range( vlength ):
                data[i] = payload[pos + i]
            pos = pos + vlength

            if( exCodeLevel == 0 ):
                if( code == 0x02 ):    # poor signal quality (0 to 255) 0=>OK; 200 => no skin contact
                    self.msd.poorSignalQuality = data[0]
                elif( code == 0x04 ):  # attention eSense (0 to 100) 40-60 => neutral, 0 => result is unreliable
                    self.msd.attentionESense = data[0]
                elif( code == 0x05 ):  # meditation eSense (0 to 100) 40-60 => neutral, 0 => result is unreliable
                    self.msd.meditationESense = data[0]
                elif( code == 0x80 ):  # raw wave value (-32768 to 32767) - big endian
                    n = ( data[0]<<8 ) + data[1]
                    if( n >= 32768 ):
                        n = n - 65536
                    self.msd.rawWave16Bit = n
                elif( code == 0x83 ):  # asic eeg power struct (8, 3 bytes unsigned int big indian)
                    self.msd.delta     = ( data[0] <<16 ) + ( data[1] <<8 ) + data[2]
                    self.msd.theta     = ( data[3] <<16 ) + ( data[4] <<8 ) + data[5]
                    self.msd.lowAlpha  = ( data[6] <<16 ) + ( data[7] <<8 ) + data[8]
                    self.msd.highAlpha = ( data[9] <<16 ) + ( data[10]<<8 ) + data[11]
                    self.msd.lowBeta   = ( data[12]<<16 ) + ( data[13]<<8 ) + data[14]
                    self.msd.highBeta  = ( data[15]<<16 ) + ( data[16]<<8 ) + data[17]
                    self.msd.lowGamma  = ( data[18]<<16 ) + ( data[19]<<8 ) + data[20]
                    self.msd.midGamma  = ( data[21]<<16 ) + ( data[22]<<8 ) + data[23]
                # elif( code == 0x01 ):  # code battery - battery low (0x00)
                # elif( code == 0x03 ):  # heart rate (0 to 255)
                # elif( code == 0x06 ):  # 8bit raw wave value (0 to 255)
                # elif( code == 0x07 ):  # raw marker section start (0)
                # elif( code == 0x16 ):  # blink strength (1 to 255)
                # elif( code == 0x81 ):  # eeg power struct (legacy float)
                # elif( code == 0x86 ):  # rrinterval (0 to 65535)
                # elif( code == 0xd0 ):  # headset (RF) found and connected
                # elif( code == 0xd1 ):  # headset (RF) not found
                # elif( code == 0xd2 ):  # headset (RF) disconnected
                # elif( code == 0xd3 ):  # headset (RF) request denied
                # elif( code == 0xd4 ):  # headset (RF) in standby/scan mode
                else:
                    print( "_parsePayload(): ExCodeLevel - %02x, Code: %02x, Data: [%s]\n" % ( exCodeLevel, code, ''.join(format(x, '02X') for x in data) ), end='' )
            else:
                print( "_parsePayload(): ExCodeLevel - %02x, Code: %02x, Data: [%s]\n" % ( exCodeLevel, code, ''.join(format(x, '02X') for x in data) ), end='' )
        self.mutex.release()
