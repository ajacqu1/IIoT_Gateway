# Liste des protocoles supportés par la passerelle.
list_fieldbus = ["canbus", "modbus"]
list_protocol_com = ["MQTT", "REST"]

### Identifications de la plateforme Thingspeak, valeurs à modifier ###

# Paramètres de connexion REST
rest_url = "https://api.thingspeak.com/"
rest_channel = ""
rest_writing_key = ""
rest_reading_key = ""
rest_user_key = ""


# Paramètres de connexion MQTT
mqtt_channel = ""
mqtt_url = "mqtt3.thingspeak.com"
mqtt_client_ID = ""
mqtt_username = ""
mqtt_password = ""

#######################################################################

### Paramètres des Fieldbus ###########################################

# Encodage des nombres décimaux
FLOAT_MODE = "bin32"
# Modbus
PORT = "/dev/ttySC0"
BAUDRATE = 57600
ADDRESS = 0x01
#Canbus
CHANNEL = "can0"
BITRATE = 125000
BUSTYPE = "socketcan"

#######################################################################

#Codes d'état MQTT
mqtt_rc = {0:"0 - Connexion réussie",
           1:"1 - Connexion refusée, version du protocole incorrecte",
           2:"2 - Connexion refusée, identifiant du client invalide",
           3:"3 - Connexion refusée, serveur non disponible",
           4:"4 - Connexion refusée, identifiant ou mot de passe invalide",
           5:"5 - Connexion refusée, accès non autorisé"}