#Instructions réalisées au lancement du programme

from ressources.communications import *
from ressources.fieldbus import *
from ressources.math import *
from ressources.interface import *
from ressources.config import *
from os import system


def instances(use_modbus=False, use_canbus=False, use_rest=False, use_mqtt=False):
    """Permet d'initialiser les différentes instances des protocoles utilisés dans le programme."""
    
    try:
        if use_modbus:
            print("Création d'une instance 'Modbus'...")
            modbus = MODBUS("Modbus", baudrate=BAUDRATE, port=PORT, address=ADDRESS, float_mode=FLOAT_MODE)
            return modbus
        if use_canbus:
            print("Création d'une instance 'Canbus'...")
            canbus = CANBUS("Canbus", bitrate=BITRATE, channel=CHANNEL, bustype=BUSTYPE, float_mode=FLOAT_MODE)
            return canbus
        if use_rest:
            print("Création d'une instance 'Rest'...")
            rest_ts = REST("rest", rest_url, rest_channel, rest_writing_key, rest_reading_key, rest_user_key, DEBUG=1)
            return rest_ts
        if use_mqtt:
            print("Création d'une instance 'Mqtt'...")
            mqtt_ts = MQTT("mqtt", mqtt_url, mqtt_channel, mqtt_username, mqtt_password, DEBUG=1)
            return mqtt_ts

            
    except Exception as e:
        print(e)

system("clear")

# Initialisation des différentes instances
modbus = instances(use_modbus=True)
canbus = instances(use_canbus=True)
mqtt_ts = instances(use_mqtt=True)
rest_ts = instances(use_rest=True)
com = COMMUNICATION(mqtt_ts) #Le protocole MQTT sera utilisé par défaut
db = DATABASE("database")
interface = INTERFACE_MOD(modbus, db, fieldbus="modbus", protocol_com=com.name) #Le protocole Modbus sera utilisé par défaut

interface.homepage()
