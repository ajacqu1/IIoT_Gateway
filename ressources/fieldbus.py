import os
import sys
sys.path.append("/home/pi/.local/lib/python3.7/site-packages")
import time
import can
import serial
from abc import ABC, abstractmethod
from pymodbus.pdu import ModbusRequest
from pymodbus.client.sync import ModbusSerialClient as ModbusClient #ModbusClient sera notre client RTU
from pymodbus.transaction import ModbusRtuFramer
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
from struct import *
from ressources.math import *
import keyboard
from ressources.communications import *

import RPi.GPIO as GPIO

import logging  #Permet d'afficher les logs et de déterminer d'où peut venir une erreur
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.ERROR) #Afficher le minimum d'information pour ne déceler uniquement les erreurs
#On peut remplacer ERROR par DEBUG pour avoir plus d'informations concernant l'envoi et la réception des frames


class FIELDBUS(ABC):
    """Classe servant de classe mère pour la création des différentes classes permettant l'implantation des divers bus de terrain.
Il est important de s'assurer de surcharger les méthodes abstraites."""
    
    @abstractmethod
    def __init__(self, name, sleeping_on = False, float_mode = "bin32"): #On surchargera l'initialisation dans les classes enfants
        
        self._name = name
        self.is_open = False
        self._sleeping_on = False
        if type(sleeping_on) == bool:
            self._sleeping_on = sleeping_on
        self._float_mode = float_mode
        
    def wake_up(self):
        """Permet de réveiller le serveur avant de lui envoyer un requête pour un échange de données. Cette fonction n'est utile que si le serveur dispose de cette fonctionnalité."""
        
        try:
            if self._sleeping_on:
                intPin = 11 #Le réveil des noeuds sera géré par le GPIO 17 (PIN 11)
                GPIO.setmode(GPIO.BOARD)
                GPIO.setup(intPin, GPIO.OUT)
                GPIO.output(intPin, GPIO.HIGH)
                GPIO.output(intPin, GPIO.LOW)
                time.sleep(0.5)
                GPIO.output(intPin, GPIO.HIGH)
                GPIO.cleanup(intPin)
            
        except Exception as e:
            print(e)
            
    def sleep(self, sleeping_on):
        """Permet d'activer ou de désactiver l'option de sommeil."""
        
        try:
            if type(sleeping_on) == bool:
                self._sleeping_on = sleeping_on
            
        except Exception as e:
            print(e)
    
    @abstractmethod
    def shutdown(self):
        pass
    
    @abstractmethod
    def set_param(self):
        pass
    
    @abstractmethod
    def get_param(self):
        pass

class MODBUS(FIELDBUS):
    """Permet de créer une instance pour simuler le bus de terrain 'Modbus'."""
    
    def __init__(self, name, baudrate=9600, port="/dev/ttySC0", address=0x01, sleeping_on = False, float_mode = "bin32"):
        self._name = name
        self._baudrate = baudrate
        self._port = port
        self._address = address
        self.is_open = False
        self._sleeping_on = False
        if type(sleeping_on) == bool:
            self._sleeping_on = sleeping_on
        
        self._float_mode = float_mode
        
        # Initialisation par défaut des registres (les valeurs sont modifiables par la fonction set_reg()
        self.set_reg(0,4,4,6,10,8)
        self._client = None
        
        #Création d'une instance modbus
        try:
            self._client = ModbusClient(method="rtu", port=self._port, stopbits=1, bytesize=8, parity='N', baudrate=self._baudrate)
            ser = serial.Serial(self._port, self._baudrate, timeout=1)
            self._wo = Endian.Big; self._bo = Endian.Big
            connexion = self._client.connect()
                
        except Exception as e:
            print("\nUne erreur est survenue...")
            print(str(e))
            
        if connexion:
            self.is_open = True
            print("Instance 'Modbus' correctement initialisée.\n")
            
        else:
            print("L'instance 'Modbus' n'as pas correctement été initialisée.\n")
        
    def __repr__(self):
        return "Instance simulant un client et permettant de communiquer avec un serveur via la norme RS485 et le protocole Modbus."
    
    def shutdown(self):
        """Permet d'arrêter proprement l'instance en cours."""
        
        self.is_open = False
        self._client.close()
        return "Instance terminée avec succès."
    
    def wake_up(self):
        """Permet de réveiller le serveur avant de lui envoyer un requête pour un échange de données. Cette fonction n'est utile que si le serveur dispose de cette fonctionnalité."""
        
        try:
            if self._sleeping_on:
                intPin = 11 #Le réveil des noeuds sera géré par le GPIO 17 (PIN 11)
                GPIO.setmode(GPIO.BOARD)
                GPIO.setup(intPin, GPIO.OUT)
                GPIO.output(intPin, GPIO.HIGH)
                GPIO.output(intPin, GPIO.LOW)
                time.sleep(0.5)
                GPIO.output(intPin, GPIO.HIGH)
                GPIO.cleanup(intPin)
                
        except Exception as e:
            print(e)
    
    def set_param(self, baudrate=None, port=None, address=None, float_mode=None):
        """Permet de modifier les différents paramètres utilisés pour la connexion avec le serveur Modbus."""
        
        try:
            assert isinstance(baudrate, (int, type(None)))
            assert isinstance(port, (str, type(None)))
            assert isinstance(address, (int, type(None)))
            
            if baudrate:
                self._baudrate = baudrate
                print("Baudrate modifié.")
            if port:
                self._port = port
                print("Port modifié.")
            if address:
                self._address = address
                print("Adresse modifiée.")
            if float_mode:
                if float_mode == "bin32" or float_mode == "frac":
                    self._float_mode = float_mode
                    print("Mode d'encodage des flottants modifié en {}.".format(self._float_mode))
                else:
                    print("Le mode d'encodage saisi n'est pas valide, aucune modification n'a été effectuée.") 
                
        except AssertionError:
            print("Les paramètres saisis ne sont rpas au bon format, aucune action n'a été effectuée.")
    
    def get_param(self):
        """Affiche les différents paramètres utilisés pour la connexion avec le serveur Modbus."""
        
        print("\nBAUDRATE : " + str(self._baudrate))
        print("PORT : " + str(self._port))
        print("ADDRESS : " + str(self._address))
        print("ENCODAGE DES FLOTTANTS : " + str(self._float_mode))
        
    
    def set_reg(self, reg_int_address, reg_int_size, reg_float_address, reg_float_size, reg_text_address, reg_text_size):
        """Permet de configurer les adresses et tailles des différents registres d'exploitation du serveur."""
        
        try:
            assert isinstance(reg_int_address, int)
            assert isinstance(reg_int_size, int)
            assert isinstance(reg_float_address, int)
            assert isinstance(reg_float_size, int)
            assert isinstance(reg_text_address, int)
            assert isinstance(reg_text_size, int)
        
            self._reg_int_address = reg_int_address
            self._reg_int_size = reg_int_size
            self._reg_float_address = reg_float_address
            self._reg_float_size = reg_float_size
            self._reg_text_address = reg_text_address
            self._reg_text_size = reg_text_size
            
            print("-> Les registres Modbus ont bien été configurés.")
            
        except AssertionError:
            print("Les paramètres saisis ne sont pas au bon format, aucune action n'a été effectuée.")
            
    def get_reg(self):
        """Affiche les adresses et tailles des différents registres d'exploitation du serveur."""
        
        print("\nAdresse du premier registre d'exploitation dédié aux int   : " + str(self._reg_int_address))
        print("Nombre de registres d'exploitation dédiés aux int          : " + str(self._reg_int_size))
        print("Adresse du premier registre d'exploitation dédié aux float : " + str(self._reg_float_address))
        print("Nombre de registres d'exploitation dédiés aux float        : " + str(self._reg_float_size))
        print("Adresse du premier registre d'exploitation dédié au texte  : " + str(self._reg_text_address))
        print("Nombre de registres d'exploitation dédiés au texte         : " + str(self._reg_text_size))
        
    def FC1(self, nb, num): #Lecture de coils
        """Permet la lecture de coils."""
        
        try:
            self.wake_up()
            result = self._client.read_coils(num, nb, unit=self._address)
            if not result.isError():
                val = [result.bits[i] for i in range(nb)]
                print("Les valeurs des coils sélectionnés sont : " + str(val) + "\n")
                return time.time(), num, val
            else:
                print("Une erreur est survenue...")
                print(str(result) + "\n")
                return None
                
        except Exception as e:
            print(e)
                
    def FC2(self, nb, num):
        """Permet la lecture d'entrées discrètes."""
        
        try:
            self.wake_up()
            result = self._client.read_discrete_inputs(num, nb, unit=self._address)
            if not result.isError():
                val = [result.bits[i] for i in range(nb)]
                print("Les valeurs des entrées discrètes sélectionnées sont : " + str(val) + "\n")
                return time.time(), num, val
            else:
                print("Une erreur est survenue...")
                print(str(result) + "\n")
                return None
                
        except Exception as e:
            print(e)
        
    def FC3(self, nb, num, typ):
        """Permet la lecture de registres d'exploitation."""
        
        try:
            if typ == int:
                self.wake_up()
                result = self._client.read_holding_registers(num,nb,unit=self._address)
                if not result.isError():
                    if nb == 1:
                        print("La valeur du registre d'exploitation {} est : ".format(num) + str(result.registers) + "\n")
                    else:
                        print("Les valeurs des registres d'exploitation {} à {} sont : ".format(num, num + nb) + str(result.registers) + "\n")
                    return time.time(), num, result.registers
                else:
                    print("Une erreur est survenue...")
                    print(str(result) + "\n")
                    return None

                    
            elif typ == float:
                num *= 2 #Les registres des float marchent par pair
                if 2*nb + num <= self._reg_float_size:
                    self.wake_up()
                    result = self._client.read_holding_registers(self._reg_float_address+num, 2*nb,  unit=self._address)
                    if not result.isError():
                        decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=self._bo, wordorder=self._wo)
                        val = []
                        for k in range(nb):
                            val.append(decoder.decode_32bit_float())
                        if nb == 1:
                            print("La valeur stockée dans le registre d'exploitation {} est ".format(num) + str(val) + "\n")
                        else:
                            print("Les valeur stockées dans les registres d'exploitation {} à {} sont ".format(num, num+nb) + str(val) + "\n")
                        return time.time(), num, val
                    else:
                        print("Une erreur est survenue...")
                        print(str(result) + "\n")
                        return None
                else:
                    print("Les données saisies sont invalides")
                    
            else:
                self.wake_up()
                if num > self._reg_text_size:
                    num = self._reg_text_size - 1            
                if num + nb <= self._reg_text_size:
                    result = self._client.read_holding_registers(self._reg_text_address+num, nb,  unit=self._address)
                else:
                    result = self._client.read_holding_registers(self._reg_text_address+num, self._reg_text_size-num, unit=self._address)
                if not result.isError():
                    decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=self._bo, wordorder=self._wo)
                    val = decoder.decode_string((self._reg_text_size-num)*2)
                    print("Le texte stocké dans les registres d'exploitation est '" + val.decode("ascii") + "' \n")
                    return time.time(), num, val.decode("ascii")
                else:
                    print("Une erreur est survenue...")
                    print(str(result) + "\n")
                    return None
                    
        except Exception as e:
            print(e)
            
    def FC4(self, nb, num, typ):
        """Permet la lecture de registres d'entrée."""
        
        try:
            if typ == int:
                self.wake_up()
                result = self._client.read_input_registers(num, nb, unit=self._address)
                if not result.isError():
                    print("Les valeurs des registres d'entrée sélectionnés sont : " + str(result.registers) + "\n")
                    return time.time(), num, result.registers
                else:
                    print("Une erreur est survenue...")
                    print(str(result) + "\n")
                    return None
                
            elif typ == float:
                print("\nAttention, cette fonction n'est à utiliser que si des floats sont reçus en entrée, sinon les résultats affichés peuvent être incohérents.")
                print("Dans l'exemple de serveur utilisé en parallèle de ce programme, les entrées discrètes sont toutes entières.")
                print("L'option est cependant tout de même présente et fonctionnelle. \n")
                self._wake_up()
                result = self._client.read_input_registers(num, 2*nb,  unit=self._address)
                if not result.isError():
                    decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=bo, wordorder=wo)
                    val = []
                    for k in range(nb):
                        val.append(decoder.decode_32bit_float())
                    if nb == 1:
                        print("La valeur stockée dans le registre d'exploitation {} est ".format(num) + str(val) + "\n")
                    else:
                        print("Les valeur stockées dans les registres d'exploitations {} à {} sont ".format(num, num+nb) + str(val) + "\n")
                    return val
                        
                else:
                    print("Une erreur est survenue...")
                    print(str(result) + "\n")
                    return None
            else:
                print("Les paramètres fournis sont invalides, veuillez réessayer.")
                
        except Exception as e:
            print(e)

    def FC5(self, num, val):
        """Permet l'écriture d"un coil."""
        
        try:
            self.wake_up()
            frame = self._client.write_coil(num, val, unit=self._address)
            if not frame.isError():
                print("La valeur " + str(val) + " a été assignée au coil sélectionné \n")
            else:
                print("Une erreur est survenue...")
                print(str(frame) + "\n")
                
        except Exception as e:
            print(e)
            
    def FC6(self, num, val, typ):
        """Permet l'écriture d"un registre d'exploitation."""
        
        try:
            if typ == int:
                if num < self._reg_int_address + self._reg_int_size: 
                    self.wake_up()
                    frame = self._client.write_register(num, val, unit=self._address)
                    if not frame.isError():
                        print("La valeur " + str(val) + " a été écrite dans le registre d'exploitation \n")
                    else:
                        print("Une erreur est survenue...")
                        print(str(frame) + "\n")
                else:
                    print("Les registres présents à cette adresse sont réservés pour une autre utilisation")
                    
            elif typ == float:
                num *= 2 #On écrit les float sur les registres pairs
                if num < self._reg_int_size - 1: #Le -1 s"explique par le fait qu'on a besoin de 2 registres pour stocker le nombre
                    builder = BinaryPayloadBuilder(byteorder=self._bo, wordorder=self._wo)
                    builder.add_32bit_float(val)
                    payload = builder.build()
                    self.wake_up()
                    frame = self._client.write_registers(self._reg_float_address+num, payload, skip_encode=True, unit=self._address)
                    if not frame.isError():
                        print("La valeur " + str(val) + " a été écrite dans le registre d'exploitation {} \n".format(num))
                    else:
                        print("Une erreur est survenue...")
                        print(str(frame) + "\n")
                else:
                    print("Les registres présents à cette adresse sont réservés pour une autre utilisation")
                    
            elif typ == str:
                builder = BinaryPayloadBuilder(byteorder=self._bo, wordorder=self._wo)
                builder.add_string(val)
                payload = builder.build()
                self.wake_up()
                frame = self._client.write_registers(self._reg_text_address+num, payload, skip_encode=True, unit=self._address)
                if not frame.isError():
                    print("Le texte '" + val + "' a été écrit dans les registres d'exploitation \n")
                else:
                    print("Une erreur est survenue...")
                    print(str(frame) + "\n")
                    
            else:
                print("Les paramètres saisis sont invalides.")
                
        except Exception as e:
            print(e)
        
    def FC15(self, num, val): #Val est une liste de int
        """Permet l'écriture de plusieurs coils."""
        
        try:
            self.wake_up()
            frame = self._client.write_coils(num, val, unit=self._address)
            if not frame.isError():
                print("Les valeurs " + str(val) + " ont été écrites dans les coils sélectionnés \n")
            else:
                print("Une erreur est survenue...")
                print(str(frame) + "\n")
                
        except Exception as e:
            print(e)
            
    def FC16(self, nb, num, val, typ):
        """Permet l'écriture de plusieurs registres d'exploitation."""
        
        try:
            if typ == int:
                if num + nb <= self._reg_int_address + self._reg_int_size:
                    self.wake_up()
                    frame = self._client.write_registers(num, val, unit=self._address)
                    if not frame.isError():
                        print("Les valeurs " + str(val) + " ont été écrites dans les registres d'exploitation sélectionnés \n")
                    else:
                        print("Une erreur est survenue...")
                        print(str(frame) + "\n")
                else:
                    print("Les registres présents à cette adresse sont réservés pour une autre utilisation")
                    
            elif typ == float:
                num *= 2 #On écrit les float sur les registres pairs
                if num + 2*nb <= self._reg_float_size:
                    builder = BinaryPayloadBuilder(byteorder=self._bo, wordorder=self._wo)
                    for k in range(nb):
                        builder.add_32bit_float(val[k])
                    payload = builder.build()
                    self.wake_up()
                    frame = self._client.write_registers(self._reg_float_address+num, payload, skip_encode=True, unit=self._address)
                    if not frame.isError():
                        print("Les valeurs " + str(val) + " ont été écrites dans les registres d'exploitation sélectionnés \n")
                    else:
                        print("Une erreur est survenue...")
                        print(str(frame) + "\n")
                else:
                    print("Les registres présents à cette adresse sont réservés pour une autre utilisation")
                    
            else:
                print("Les paramètres saisis sont invalides.")
                
        except Exception as e:
            print(e)                  

        
class CANBUS(FIELDBUS):
    """Permet de créer une instance pour simuler le bus de terrain 'Canbus'."""
    
    def __init__(self, name, bitrate=125000, channel="can0", bustype="socketcan", float_mode="bin32"):
        self._name = name
        self._bitrate = bitrate
        self._channel = channel
        self._bustype = bustype
        self._float_mode = float_mode
        self._bus = False
        self.is_open = False
        self._sleeping_on = False
        
        try:
            os.system("sudo ip link set {} type can bitrate {}".format(self._channel, self._bitrate))
            os.system("sudo ifconfig {} up".format(self._channel))
            self._bus = can.interface.Bus(channel = self._channel, bustype = self._bustype)
            
        except NotImplementedError as e:
            print("Une erreur est survenue...")
            print(str(e))
            os.system("sudo ifconfig {} up".format(self._channel))
            
        except Exception as e:
            print("Une erreur est survenue...")
            print(str(e))
            os.system("sudo ifconfig {} up".format(self._channel))
            
        if self._bus:
            self.is_open = True
            print("Instance 'Canbus' correctement initialisée.\n")
        
        else:
            print("L'instance 'Canbus' n'as pas correctement été initialisée.\n")        
        
    def __repr__(self):
        return "Instance permettant de communiquer avec les différents appareils d'un bus de données CAN."
    
    def shutdown(self):
        """Permet d'arrêter proprement l'instance en cours."""
        
        os.system("sudo ifconfig {} down".format(self._channel))
        self.is_open = False
        return "Instance terminée avec succès."
    
    def set_param(self, bitrate=None, channel=None, bustype=None, float_mode=None):
        """Permet de modifier les différents paramètres utilisés pour la connexion sur le bus CAN."""
        
        try:
            assert isinstance(bitrate, (int, type(None)))
            assert isinstance(channel, (str, type(None)))
            assert isinstance(bustype, (int, type(None)))
            assert isinstance(float_mode, (str, type(None)))
        
            if bitrate:
                self._bitrate = bitrate
                print("Bitrate modifié à {}.".format(self._bitrate))
            if channel:
                self._channel = channel
                print("Chaine modifiée en {}.".format(self._channel))
            if bustype:
                self._bustype = bustype
                print("Type de bus modifié en {}.".format(self._bustype))
            if float_mode:
                if float_mode == "bin32" or float_mode == "frac":
                    self._float_mode = float_mode
                    print("Mode d'encodage des flottants modifié en {}.".format(self._float_mode))
                else:
                    print("Le mode d'encodage saisi n'est pas valide, aucune modification n'a été effectuée.")                
                
        except AssertionError:
            print("Les paramètres saisis ne sont pas au bon format, aucune action n'a été effectuée.")
    
    def get_param(self):
        """Affiche les différents paramètres utilisés pour la connexion sur le réseau CAN."""
        
        print("\nBITRATE : " + str(self._bitrate))
        print("CHAINE : " + str(self._channel))
        print("TYPE DE BUS : " + str(self._bustype))
        print("ENCODAGE DES FLOTTANTS : " + str(self._float_mode))
        
    def rcv(self, timeout=None, ID=None):
        """Permet d'écouter et de recevoir les messages transmis sur le bus."""
        
        try:
#             if ID:  #N'est pas valable pour les extended_id, il faut alors continuer les incrémentations.
#                 if len(ID) == 1:
#                     can_mask = 0xF
#                 elif len(ID) == 2:
#                     can_mask == 0xFF
#                 elif len(ID) == 3:
#                     can_mask = 0xFFF
#                 else:
#                     can_mask = 0xFFFF
#                 self._bus.set_filters([{"can_id":ID, "can_mask":can_mask, "extended":False}])
#                 
            frame = self._bus.recv(timeout=timeout)
            if frame:
                if frame.is_remote_frame:
                    print("Une requête de frame a été émise par un appareil du bus concernant l'ID {}.".format(frame.arbitration_id))
                    
                    ##########
                    
                    # Ecrire ici le code pour choisir comment gérer ces requêtes. Cela est à définir par l'utilisateur.
                    
                    ##########
                
                else:
                    
                    #Valeurs arbitraires qui peuvent être changées selon les besoins de l'utilisateur
                    new_value = None
                    if frame.arbitration_id >= 500 and frame.arbitration_id < 600: #Concerne les floats
                        new_value = float_decode(self._float_mode, list(frame.data))
                        
                    
                    elif frame.arbitration_id >= 600 and frame.arbitration_id < 700: #Concerne les strings
                        new_value = int_to_text(list(frame.data))
                    self._bus.set_filters()    
                    return(frame, new_value)

                
        except KeyboardInterrupt:
            time.sleep(0.1)
            
        except Exception as e:
            print("Une erreur est survenue : " + str(e) + "\n")
            time.sleep(0.1)
            
    def send(self, ID, data, ext_id=False): #Extended ID n'est pas compatible avec l'exemple Arduino utilisé pour le développement, les frames ne seront pas reçues.
        """Permet d'envoyer un message sur le bus."""
        
        try:
            if isinstance(data, list):
                frame = can.Message(arbitration_id=ID, data=data, extended_id=ext_id)
                
            elif isinstance(data, float):
                data = float_encode(self._float_mode, data)
                frame = can.Message(arbitration_id=ID, data=data, extended_id=ext_id)
            
            elif isinstance(data, str):
                data = text_to_int(data)
                list_data = text_split(data, lenght=8)
                for data in list_data:
                    frame = can.Message(arbitration_id=ID, data=data, extended_id=ext_id)
            
            elif isinstance(data, int):
                data = to_list(data)
                frame = can.Message(arbitration_id=ID, data=data, extended_id=ext_id)
            
            else:
                print("Le format des données d'entrée est invalide, veuillez réessayer.")
            
            self.wake_up()
            
            try:
                self._bus.send(frame)
                print("{} envoyé avec l'ID {}.".format(list(frame.data), frame.arbitration_id))
            except can.CanError as err:
                print("Une erreur est survenue...")
                print(err)
            
        except KeyboardInterrupt:
            self.shutdown()
            time.sleep(0.1)
    
        except Exception as e:
            print("Une erreur est survenue : " + str(e) + "\n")
            time.sleep(0.1)
            
    def send_cyclic(self, ID, data, period, end_time = None, ext_id=False): # Les floats et strings ne sont pas implantés dans cette fonction
        """Permet d'envoyer un message de manière cyclique sur le bus."""
        
        try:
            
            frame = can.Message(arbitration_id=ID, data=data, extended_id=ext_id)
            self.wake_up()
            task = self._bus.send_periodic(frame, period)
            
            assert isinstance(task, (can.CyclicSendTaskABC, can.ModifiableCyclicTaskABC))
            
            if end_time:
                time.sleep(end_time)
                task.stop()
                print("La transmission cyclique s'est correctement achevée.")
                
            if not end_time:
                print("La trame de données est actuellement envoyée de manière cyclique...")
                
                while not end_time:
                    
                    try:
                        print("Veuillez choisir l'action à effectuer en saisissant le numéro correspondant :")
                        print("Interrompre la communication cyclique.        (1)")
                        print("Modifier les données de la trame transmise.   (2)")
                        action = int(input())
                        
                        if action == 1:
                            task.stop()
                            print("La transmission cyclique s'est correctement achevée.\n")
                            return None
                            
                        elif action == 2:
                            lenght = int(input("Veuillez indiquer le nombre d'octets à transmettre (max 8) : "))
                            if lenght > 0 and lenght <= 8:
                                frame.dlc = lenght
                                for i in range(lenght):
                                    val = int(input("Valeur de l'octet {} (0 à 255) : ".format(i)))
                                    if val < 0 or val > 255:
                                        print("La valeur saisie n'est pas valide, veuillez recommencer le processus.")
                                    frame.data[i] = val
        
                            else:
                                print("La longueur choisie est invalide.\n")
                                
                            print("Modification de la trame...")
                            task.modify_data(frame) 
                            
                        else:
                            print("Erreur, les données sont invalides.\n")
                            
                    except KeyboardInterrupt:
                        self.shutdown()
                        time.sleep(0.1)
                
                    except Exception as e:
                        print("Une erreur est survenue : " + str(e) + "\n")
                        time.sleep(0.1)

        
        except AssertionError:
            task.stop()
            print("L'interface utilisée actuellement ne supporte pas ce type de communications.")
            
        except KeyboardInterrupt:
            self.shutdown()
            time.sleep(0.1)
    
        except Exception as e:
            print("Une erreur est survenue : " + str(e) + "\n")
            time.sleep(0.1)
                        
    def remote(self, ID, ext_id=False):
        """Permet d'envoyer une requête de trame à distance."""
        
        try:
            frame = can.Message(arbitration_id=ID, extended_id=ext_id, is_remote_frame=True)
            self.wake_up()
            self._bus.send(frame)
            print("La requête de frame à distance a été correctement transmise avec l'ID {}.\n".format(frame.arbitration_id))
            
        except Exception as e:
            print("Une erreur est survenue : " + str(e) + "\n")
            time.sleep(0.1)
            
    
    def listen(self, ID=None, db=None):
        """Permet de d'écouter le bus pour afficher tous les messages circulant sur ce dernier ayant une ID quelconque ou spécifique."""
        
        print("Début de l'écoute (Vous pouvez arrêter l'écoute à tout moment en appuyant sur 'Echap').")
        run = True

        while run:
            try:
                assert isinstance(db, (DATABASE, type(None)))
                frame = self.rcv(timeout=0.1)
                
                if keyboard.is_pressed("esc"):
                    print("Fin de l'écoute.")
                    run = False
                if frame:
                    if frame[0].arbitration_id == ID or ID == None:
                        result = MESSAGE_CAN(frame)
                        print(result)
                        if db:
                            db.add(result)
#                             if interface._auto_sync: #Implantation mise de côté car Thingspeak n'autorise qu'une valeur toutes les 15 sec.
#                                 result.sync(mqtt_ts)
                    
                    
            except KeyboardInterrupt:
                time.sleep(1)
                print("Fin de l'écoute.")
                break
            
            except Exception as e:
                print(e)
                
class MESSAGE(ABC):
    """Il s'agit ici du format de base d'un message. Cette classe est un patron de conception, les opérations spécifiques aux différents protocoles doivent être redéfinies dans les classes appropriées."""

    @abstractmethod
    def __init__(self, timestamp, topic, value):
        
        try:
            assert isinstance(timestamp, float) and isinstance(topic, str) and isinstance(value, (int, float, str)), "AssertionError : Les données saisies n'ont pas le bon format."
            
            self.is_sync = False
            
            self.timestamp = timestamp
            self.topic = topic
            self.value = value
            
        except AssertionError as a:
            print(a)
            
    @abstractmethod
    def mapping(self):
        """Cette méthode doit être surchargée dans les classes enfants."""
        pass
            
    def __str__(self):
        result = "____________________________________________________________\n"
        result += "Timestamp : " + str(self.timestamp)
        result += "\nChamp : " + str(self.topic)
        result += "\nValeur : " + str(self.value)
        result += "\n____________________________________________________________\n"
        return (result)
    
    def sync(self, protocol_com):
        """Permet de communiquer avec le service infonuagique afin téléverser les données récoltées sur le bus."""
        
        try:
            if not self.is_sync:
                
                self.mapping()
                data = {}
                if type(self.topic) == list:
                    for i in range(len(self.topic)):
                        data["field" + str(self.topic[i])] = str(self.value[i])
                else:
                    data["field" + str(self.topic)] = str(self.value)
                    
                if protocol_com.type == "mqtt":
                    request = protocol_com.pub(data)
                    
                    if request:
                        print("Données synchronisées via mqtt.")
                        self.is_sync = True
                    else :
                        print("Erreur lors de la synchronisation des données.")
                    
                elif protocol_com.type == "rest":
                    request = protocol_com.write(data)
                    if request:
                        print("Données synchronisées via rest.")
                        self.is_sync = True
                    else :
                        print("Erreur lors de la synchronisation des données.")
                
                else:
                    print("Erreur : le type de protocole défini n'est pas valide.")
                        
        except Exception as e:
            print(e)
    
    
class MESSAGE_MOD(MESSAGE):
    """Classe enfant de la classe 'MESSAGE' permettant la prise en charge du protocole 'Canbus'."""
    
    def __init__(self, frame):
        
        try:
            self.is_sync = False
            
            self.timestamp = frame[0]
            if len(frame[2]) == 1:
                self.topic = frame[1]
                self.value = frame[2][0]
            else:
                self.topic = []
                self.value=[]
                for i in range(len(frame[2])):
                    self.topic.append(int(frame[1])+i)
                    self.value.append(frame[2][i])                
            
            
        except Exception as e:
            print(e)
            
    def mapping(self):
        """Permet d'associer le topic du message d'un point de vue 'bus de terrain' qui est l'adresse du registre, au topic tel qu'il sera présenté au cloud."""
        #Il est possible de réaliser n'importe quelle association avec cette fonction...
        #L'exemple ci-dessous est purement arbitraire
        
        try:
            if type(self.topic) == int:
                self.topic += 1 #On réalise cette action car les adresses Modbus sont indexées à partir de 0 et les champs Thingspeak à partir de 1
            else:
                for i in range(len(self.topic)):
                    self.topic[i] += 1
                
        except Exception as e:
            print(e)
    

class MESSAGE_CAN(MESSAGE):
    """Classe enfant de la classe 'MESSAGE' permettant la prise en charge du protocole 'Canbus'."""
    
    def __init__(self, data):
        
        try:
            frame, new_value = data
            
            self.is_sync = False
            self.timestamp = frame.timestamp
            
            if new_value:
                self.value = new_value
                self.topic = frame.arbitration_id
                
            else:
                self.value = list(frame.data)
                if len(self.value) == 1:
                    self.topic = frame.arbitration_id
                    self.value = self.value[0]
                
                else:
                    self.topic = frame.arbitration_id
                    self.value = list(frame.data) 
            
            
        except Exception as e:
            print(e)

    def mapping(self):
        """Permet d'associer le topic du message d'un point de vue 'bus de terrain' qui est l'adresse du registre, au topic tel qu'il sera présenté au cloud."""
        #Il est possible de réaliser n'importe quelle association avec cette fonction...
        #L'exemple ci-dessous est purement arbitraire
        
        try:
            if self.topic == 555:
                self.topic = 2
                
        except Exception as e:
            print(e)
        