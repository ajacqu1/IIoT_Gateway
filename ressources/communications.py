from abc import ABC, abstractmethod
import requests
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import time
import datetime
import csv
import ssl
import json
from ressources.config import *

class COMMUNICATION: # Cette classe sert de classe mère pour l'ensemble des protocoles IoT
    """Classe représentant un protocole général pour communiquer avec le service infonuagique."""
    
    def __init__(self, protocol=None, DEBUG=0):
        
        try:
            self.protocol = protocol
            self.name = None
            if protocol is not None:
                self.name = protocol._name
                
            self._DEBUG = DEBUG
            
        except Exception as e:
            print(e)
    
    def __repr__():
        pass
    
    def select(self, protocol):
        self.protocol = protocol
        self.name = protocol._name
        
    def set_debug(self, mode):
        """Permet d'activer ou non le mode DEBUG et d'afficher des informations supplémentaires."""
        
        if mode == 0:
            self._DEBUG = 0
            print("Le mode DEBUG est désactivé.")
        elif mode == 1:
            print("Le mode DEBUG est activé")
        else:
            print("Les données rentrées sont invalides, aucune modification n'a été effectuée.")

class REST(COMMUNICATION): # Veuillez vérifier l'organisation des liens URL de la plateforme IoT utilisée, ceux ci peuvent varier suivant les plateformes
    """Architechture de communication basée sur des requêtes HTTP pour permettre la communication avec le service infonuagique."""
    
    def __init__(self, name, url, channel, writing_key, reading_key, user_key, DEBUG=0):
        
        try:
            self._name = name
            self.type = "rest"
            self._url = url
            self._channel = channel
            self._writing_key = writing_key
            self._reading_key = reading_key
            self._user_key = user_key
            self._DEBUG = DEBUG
            
            #Initialisation des url de requête par défaut
            self.set_url(param="init")
            
            print("Instance 'REST' correctement initialisée.\n")
            
        except Exception as e:
            print(e)
            print("L'instance 'REST' n'a pas correctement été initialisée.")
        
        
    def __repr__(self):
        return "API REST pour communiquer avec le service {}.".format(self._name)
    
    def set_debug(self, mode):
        """Permet d'activer ou non le mode DEBUG et d'afficher des informations supplémentaires."""
        
        if mode == 0:
            self._DEBUG = 0
            print("Le mode DEBUG est désactivé.")
        elif mode == 1:
            print("Le mode DEBUG est activé")
        else:
            print("Les données rentrées sont invalides, aucune modification n'a été effectuée.")
    
    
    def write(self, Wdata, JSON=None):
        """Permet d'ajouter des valeurs aux champs sélectionnés."""        
        
        try:
            if not JSON:
                req = requests.post(self._url_w, data=Wdata)
            else:
                req = requests.post(self._url_w_json, data=Wdata)
            if req.ok:
                if self._DEBUG == 1:
                    print("La requête a été effectuée avec succès.")
                    print("Code d'état : {} \n".format(req.status_code))
                return True
            else:
                if self._DEBUG == 1:
                    print("La requête n'a pas abouti.")
                    print("Code d'état : {} \n".format(req.status_code))
                return False
            
        except requests.exceptions.RequestException as e:
            print("Une erreur est survenue...")
            print(str(e) + "\n")
        
            
            
    def read(self, param, ID=None, Extract = False):
        """
        Renvoie les données désirées sous le format JSON.
        param=0 : Toutes les valeurs de chaque champ de la chaine.
        param=1 : Toutes les valeurs d'un champ spécifique.
        param=2 : Dernières valeurs des différents champs de la chaine.
        param=3 : Dernière valeur d'un champ spécifique.
        ID : ID de champ
        """
        
        try:
            if param == 0:
                url = self._url_r + "/feeds.json?api_key=" + self._reading_key
            elif param == 1:
                if ID == None:
                    print("Erreur, aucun champ n'a été sélectionné")
                    return -1
                else:
                    url = self._url_r + "/fields/" + str(ID) + ".json?api_key=" + self._reading_key
            elif param == 2:
                url = self._url_r + "/feeds/last.json?api_key=" + self._reading_key
            elif param == 3:
                if ID == None:
                    print("Erreur, aucun champ n'a été sélectionné")
                    return -1
                else:
                    url = self._url_r + "/fields/" + str(ID) + "/last.json?api_key=" + self._reading_key
                    
            req = requests.get(url)
            if self._DEBUG == 1:
                if req.ok:
                    print("La requête a été effectuée avec succès.")
                    print("Code d'état : {} \n".format(req.status_code))
                    return req.json()
                else:
                    print("La requête n'a pu aboutir.")
                    print("Code d'état : {} \n".format(req.status_code))
                    return -1
            else:
                if req.ok:
                    return req.json()
                else:
                    return -1
        
        except Exception as e:
            print("Une erreur est survenue...")
            print(str(e) + "\n")
            
    def extract(self, param, champ, ID=None, extract=True):
        """Renvoie la dernière valeur du champ sélectionné."""
        
        rep = self.read(param, ID, extract)
        if rep == -1:
            return rep
        val = []
        if param == 0 or param == 1:
            for i in rep["feeds"]:
                val.append(float(i[champ]))
        else:
            val = rep[champ]
        return val
    
    def clear(self):
        """Permet de supprimer toutes les données de la chaine."""
        
        req = requests.delete(self._url_c)
        if self._DEBUG == 1:
            if req.ok:
                print("La requête a été effectuée avec succès.")
                print("Code d'état : {} \n".format(req.status_code))
            else:
                print("La requête n'a pu aboutir.")
                print("Code d'état : {} \n".format(req.status_code))
                
    def set_url(self, param, url=""):
        """
        Permet de modifier les url de requêtes HTTP par défaut.
        param="init" : Réinitialiser les url par défaut."
        param="w" : Définir l'url utilisée pour la fonction POST.
        param="r" : Définir l'url utilisée pour la fonction GET.
        param="c" : Définir l'url utilisée pour la fonction DELETE.
        """
        
        if param == "init":
            self._url_w = self._url + "update?api_key=" + self._writing_key
            self._url_w_json = self._url + "update.json"
            self._url_r = self._url + "channels/" + self._channel
            self._url_c = self._url + "channels/" + self._channel + "/feeds.json?api_key=" + self._user_key
        elif param == "w":
            self._url_w = str(url)
        elif param == "r":
            self._url_r = str(url)
        elif param == "c": 
            self._url_c = str(url)
        else:
            print("Paramètre invalide, veuillez réessayer.")
            
    def get_url(self):
        """Affiche les différentes url utilisées pour les requêtes HTTP."""
        
        print("Url POST : " + self._url_w)
        print("Url GET : " + self._url_r)
        print("Url DELETE : " + self._url_c)

class MQTT(COMMUNICATION):
    """Protocole de communication pour échanger des données avec un service infonuagique sur la base du principe pub/sub."""
    
    def __init__(self, name, url, channel, username, password, DEBUG=0):
        self._name = name
        self.type = "mqtt"
        self._url = url
        self._channel = channel
        self._username = username
        self._password = password
        self._pubtopic = "channels/" + self._channel + "/publish"
        self._subtopic = "channels/" + self._channel + "/subscribe"
        self._DEBUG = DEBUG
        
        #Initialisation du mode de communication par défaut
        self.set_mode()
        
        print("Instance 'Mqtt' correctement initialisée.\n")
        
    def __repr__(self):
        return "Instance permettant de communiquer avec le service {} via le protocole MQTT.".format(self._name)
        
    def pub(self, data, num_field = None):
        """Permet de publier/téléverser les données souhaitées. Formats acceptés : dict, list, int ou float."""
        
        try:
            Payload = ""
            
            pubtopic = self._pubtopic
            if num_field:
                pubtopic += "/fields/field" + str(num_field)
                if type(data) == int or type(data) == float:
                    Payload = str(data)
                else:
                    return "Erreur, les données sont invalides"
                
            else:
                if type(data) == dict:
                    for i in data:
                        Payload += "&" + i + "=" + str(data[i])
                elif type(data) == list:
                    for i in range(len(data)):
                        Payload += "&field{}={}".format(i+1, data[i])  
                else:
                    return "Erreur, les données sont invalides"  
                Payload = Payload[1:] #On enlève le premier caractère "&"
                
            if Payload != "":
                
                self._rc = 0
                def on_connect(client, userdata, flags, rc):
                    self._rc =  rc
                #Connexion avec le broker
                client = mqtt.Client(client_id=self._username, clean_session=True, userdata=None, protocol=4, transport=self._Transport)
                client.on_connect = on_connect
                client.username_pw_set(username=self._username, password=self._password)
                if self._TLS is not None:
                    client.tls_set(ca_certs="/home/pi/Desktop/MQTT/certs/thingspeak.crt") #Le fichier et le chemin sont à modifier par l'utilisateur
                client.connect(host=self._url, port=self._Port)
                
                client.loop_start()
                i=0
                while ((not client.is_connected()) and i<50) and self._rc == 0:
                    time.sleep(0.1)
                    i+=1

                    
                if client.is_connected():                    
                    message = client.publish(topic=pubtopic, payload=Payload)
                    client.loop_stop()
                    client.disconnect()
                    if self._DEBUG:
                        print("La requête a été effectuée avec succès.")
                        print("Code d'état : {}.\n".format(mqtt_rc[self._rc]))
                    if message.is_published():
                        return True
                    
                else:
                    if self._DEBUG:
                        print("La requête n'a pu aboutir.")
                        print("Code d'état : {}.\n".format(mqtt_rc[self._rc]))
                    client.loop_stop()
                    client.disconnect()
                        

            
        except Exception as e:
            print(e)
            client.loop_stop()
            client.disconnect()
            
        except KeyboardInterrupt:
            client.loop_stop()
            client.disconnect()

            
    def set_mode(self, nb=0):
        """
        Permet de choisir le mode de communication avec le serveur à adopter.
        0 : TCP non sécurisé
        1 : Websocket non sécurisé
        2 : TCP sécurisé via TLS/SSL
        3 : Websocket sécurisé via TLS/SSL
        """
        
        if nb == 0:
            self._Transport = "tcp"
            self._Port = 1883
            self._TLS = None
            print("-> Mode de communication MQTT : tcp non sécurisé.")
        elif nb == 1:
            self._Transport = "websockets"
            self._Port = 80
            self._TLS = None
            print("-> Mode de communication MQTT : websocket non sécurisé. ")
        elif nb == 2:
            self._Transport = "tcp"
            self._Port = 8883
            self._TLS = {"ca_certs":"/home/pi/Desktop/MQTT/certs/thingspeak.crt"}
            print("-> Mode de communication MQTT : tcp sécurisé via TLS/SSL.")
        elif nb == 3:
            self._Transport = "websockets"
            self._Port = 443
            self._TLS = {"ca_certs":"/home/pi/Desktop/MQTT/thingspeak.crt"}
            print("-> Mode de communication MQTT : websocket sécurisé via TLS/SSL.")
        else:
            print("Le mode de communication choisi n'est pas valide, aucune modification n'a été effectuée.")
    
    def get_mode(self):
        """Affiche le mode de communication présentement utilisé"""
        
        if self._TLS == None:
            print("Mode de communication : " + self._Transport + " non sécurisé.")
        else:
            print("Mode de communication : " + self._Transport + "sécurisé via TLS/SSL.")
        print("Port de communication : {}.\n".format(self._Port))
                  
    def set_pubtopic(self, name):
        """Permet de définir le topic de publication."""
        
        self._pubtopic = str(name) #"channels/" + channel + "/publish" pour une chaine et #"channels/" + channel + "/publish/fields/field" + num_field pour un champ
       
    def get_pubtopic(self):
        """Affiche le topic de publication présentement utilisé."""
        
        print(self._pubtopic)
        
    def sub(self, sub_time, extract = None):
        """Permet de s'abonner à un topic. Les données sont transmises sous le format JSON."""
        
        try:
            #On définit les différentes fonctions utilisateurs
            def on_connect(client, userdata, flags, rc):
                print("La connexion avec le serveur a été effectuée.")
                print("Code : " + str(rc))
                client.subscribe(self._subtopic)
            def on_disconnect(client, userdata, flags):
                print("La connexion avec le broker a été interrompue.")
            def on_message(client,userdata,msg):
                data_JSON = json.loads(msg.payload.decode("utf_8")) #Convertit le string reçu en format JSON.
                if extract:
                    val = []
                    for i in data_JSON:
                        if "field" in str(i) and data_JSON[i]:
                            val.append(data_JSON[i])
                    print(val)
                else:
                    print(data_JSON)
                    
            #Connexion avec le broker
            client = mqtt.Client(client_id=self._username, clean_session=True, protocol=4)
            client.username_pw_set(username=self._username, password=self._password)
            client.on_connect = on_connect
            client.on_message = on_message
            client.on_disconnect = on_disconnect
            client.connect(self._url, port=1883)
            if sub_time == -1:
                client.loop_forever()
            else:
                client.loop_start()
                time.sleep(sub_time)
            client.loop_stop()
            client.disconnect()
            
        except Exception as e:
            print(e)
            client.loop_stop()
            client.disconnect()
            
        except KeyboardInterrupt:
            client.loop_stop()
            client.disconnect()
            
    def set_subtopic(self, name):
        """Permet de définir le topic d'abonnement."""
        
        self._subtopic = str(name) #"channels/" + self._channel + "/subscribe" pour une chaine et #"channels/" + channel + "/subscribe/fields/field" + num_field pour un champ
       
    def get_subtopic(self):
        """Affiche le topic d'abonnement présentement utilisé."""
        
        print(self._subtopic)
        
        
class DATABASE:
    """Base de donnée inclue au programme permettant de recenser les différents messages reçus depuis le début de l'éxection."""
    
    def __init__(self, name):
        self._name = name
        self.data = []
        
    def __str__(self):
        result = "timestamp\t\ttopic\t\tvalue\t\tsync"
        for i in self.data:
            result += "\n" + str(i.timestamp) + "\t\t" + str(i.topic) + "\t\t" + str(i.value) + "\t\t" + str(i.is_sync)
        return result
    
    def filter_unsync(self):
        result = "timestamp\t\ttopic\t\tvalue\t\tsync"
        for i in self.data:
            if not i.is_sync:
                result += "\n" + str(i.timestamp) + "\t\t" + str(i.topic) + "\t\t" + str(i.value) + "\t\t" + str(i.is_sync)
        return result
    
    def add(self, message):
        """Permet d'ajouter un message à la base de données."""

        try:
            self.data.append(message)
        except Exception as e:
            print(a)
    
    def get_date(self, epoch_time):
        """Permet de convertir la date au format %Y-%m-%d"""
        
        try:
            x = time.strftime("%Y-%m-%d", time.localtime(epoch_time))
            return(str(x))
        
        except Exception as e:
            print(e)
            
    def get_time(self, epoch_time):
        """Permet de convertir le temps au format %H:%M:%S""" 
        
        try:
            x = time.strftime("%H:%M:%S", time.localtime(epoch_time))
            return(str(x))
        
        except Exception as e:
            print(e)
    
    def to_csv(self, csv_name="data.csv"):
        """Permet d'exporter la base de données générer lors de l'execution du programme en csv."""
        
        try:
            with open(csv_name, mode="a") as values:
                data_write = csv.writer(values, delimiter = ",")
                for i in self.data:
                    w = data_write.writerow([self.get_date(i.timestamp), self.get_time(i.timestamp), i.topic, i.value, i.is_sync])
                return(w)
            
        except Exception as e:
            print(e)
            
    def to_json(self, protocol_com=None, topic=None):
        
        try:
            api_key = rest_writing_key
            for i in self.data:
                if not i.is_sync:
                    if not topic:                    
                        created_at = self.get_date(i.timestamp) + "T" + self.get_time(i.timestamp) + " -04:00" #Dépend du fuseau horaire de l'utilisateur
                        field = "field" + str(i.topic)
                        json_data = json.loads(json.dumps({"api_key":api_key, field:i.value, "created_at":created_at}))
                        if protocol_com.type == "rest":
                            print(i)
                            req = protocol_com.write(Wdata=json_data, JSON=True)
                            if req:
                                i.is_sync = True
                        else:
                            print("Cette fonctionnalité n'est disponible que via les requêtes HTTP. Merci de bien vouloir sélectionner le protocole REST.")
                            print("Aucune synchronisation effectuée")
                            
                    else:
                        if i.topic == topic:
                            created_at = self.get_date(i.timestamp) + "T" + self.get_time(i.timestamp) + " -04:00" #Dépend du fuseau horaire de l'utilisateur
                            field = "field" + str(i.topic)
                            json_data = json.loads(json.dumps({"api_key":api_key, field:i.value, "created_at":created_at}))
                            if protocol_com.type == "rest":
                                print(i)
                                req = protocol_com.write(Wdata=json_data, JSON=True)
                                if req:
                                    i.is_sync = True
                            else:
                                print("Cette fonctionnalité n'est disponible que via les requêtes HTTP. Merci de bien vouloir sélectionner le protocole REST.")
                                print("Aucune synchronisation effectuée")
            
            
        except Exception as e:
            print(e)
    
    def clearall(self):
        """Permet de supprimer toutes les entrées de la base de données."""
        
        try:
            self.data = []
            
        except Exception as e:
            print(e)
        
    def function(self, fct, protocol_com):
        """Recense les différentes fonctions qu'il est possible d'effectuer avec la base de données et permet d'effectuer le pont entre l'interface et la base de données."""
        
        try:
            if fct == 11:
                print(self)
                
            elif fct == 12:
                csv_name = input("Nom du fichier dans lequel écrire : ")
                csv_name += ".csv"
                self.to_csv(csv_name)
                print("Exportation terminée avec succès.")
            
            elif fct == 13:
                self.clearall()
                print("La base de données a correctement été réinitialisée.")
                
            elif fct == 21:
                pass
                
            elif fct == 22:
                print(self.filter_unsync())
                
            elif fct == 23:
                topic = input("Topic spécifique à synchroniser (laissez ce champ vide pour tout synchroniser) : ")
                if topic == "":
                    topic = None
                else:
                    topic = int(topic)
                self.to_json(protocol_com=protocol_com, topic=topic)
            
        except Exception as e:
            print(e)