import json
from os import system
import keyboard
from ressources.fieldbus import *
from termios import tcflush, TCIFLUSH

#Les différents des interfaces ne sont actuellement disponibles qu'en français
class INTERFACE: # Structure générale servant de base aux adaptateurs d'interface
    
    def __init__(self, db=None, fieldbus=None, protocol_com=None, clear=True):
        """
        Cette classe représente une interface "générale", ce sont les adaptateurs qui doivent être utilisés lorsqu'un Fieldbus est actif.
        """
        self._fieldbus = fieldbus
        self._protocol_com = protocol_com
        self._clear = clear
        self.db = db
            
        self._type_reg = None
        self._type_reg_str = None
        if self._fieldbus == "modbus":
            self.type_reg()
            
        self._auto_sync = True
        
        
    def __repr__(self):
        return "Instance permettant de gérer l'affichage du panneau de contrôle du réseau {}.".format(self._fieldbus)

    
    def clear(self):
        """Permet d'effacer les informations écrites dans la console."""
        
        try:
            if self._clear:
                return system("clear")
            
        except Exception as e:
            print(e)
    
    def menu_config(self):
        """Affiche le menu de configuration."""
        
        print("MENU CONFIGURATION\n")
        print("Veuillez choisir une option dans la liste suivante : ")
        print("- Fieldbus.          (1)")
        print("- Communication.     (2)")
        print("- A propos.          (3)")
        print("- Retour au menu.    (x)")
        
        try:
            while True:
                self.flush()
                nb = input("Veuillez choisir une option : ")
                
                if nb == "x":
                    return nb
                elif nb == "1":
                    print("\nOptions disponibles :")
                    print("- Modifier le bus de terrain utilisé.              (1)")
                    print("- Modifier les options de réveil de l'appareil.    (2)")
                    print("- Revenir au menu précédent.                       (x)")
                    loop = True
                    while loop:
                        opt = input("Veuillez choisir une option : ")
                        
                        if opt == "1":
                            print("\nLe bus de terrain actuellement utilisé est {}.".format(self._fieldbus))
                            new = input("Si vous souhaitez changer de bus de terrain, veuillez indiquer le nouveau nom, sinon laissez le champ vide : ")
                            if new != "":
                                self._fieldbus = new
                                print("La passerelle est maintenant configurée pour communiquer avec le protocole {}.".format(self._fieldbus))
                                return "bus", new
                            return
                        
                        elif opt == "2":
                            if self._fieldbus == "modbus":
                                return "sleep", 0
                            else:
                                print("Cette fonctionnalité n'est pas disponible pour le protocole en cours d'utilisation.")
                                self.wait()
                                return
                                
                        elif opt == "x":
                            loop = False
                            return
                            
                        
                elif nb == "2":
                    print("\nLe protocole de communication actuellement utilisé pour communiquer avec le service infonuagique est {}.".format(self._protocol_com))
                    new = input("Si vous souhaitez changer de protocole, veuillez indiquer le nouveau nom, sinon laissez le champ vide : ")
                    if new != "":
                        self._protocol_com = new
                        print("La passerelle est maintenant configurée pour communiquer avec le protocole {}.".format(self._protocol_com))
                        return "com", 0
                    return 
                
                elif nb == "3":
                    print("\nSection en cours de rédaction...\n")
                    time.sleep(1)
                    return
                
                else:
                    print("\nErreur dans la sélection de l'action. Veuillez réessayer.")
                    
        except Exception as e:
                print(e)
    
    def homepage(self):
        """Affiche dans la console le message de bienvenue."""
        
        print("\n\n##################################################")
        print("#   Interface de contrôle de la passerelle IoT   #")
        print("##################################################\n\n")
        
        print("Bus de terrain en cours d'utilisation : {}.".format(self._fieldbus))
        print("Protocole de communication avec le service infonuagique en cours d'utilisation : {}.\n".format(self._protocol_com))
        
    
    def home(self):
        """Affiche le menu principal."""
        
        self.clear()
        print("MENU PRINCIPAL\n")
        print("- Configuration de la passerelle                (1)")
        print("- Communication sur le bus                      (2)")
        print("- Base de données et service infonuagique       (3)")
        print("- Terminer le programme                         (x)")
        self.flush()
        while True:
            num = input("Veuillez choisir une option : ")
            if num in ["1","2","3","x"]:
                return num
            
            else:
                print("\nErreur dans la sélection de l'action. Veuillez réessayer.")
        
        return num
      
    def flush(self):
        """Permet de vider le buffer des touches pressées."""
        
        return tcflush(sys.stdin, TCIFLUSH)
    
    def wait(self):
        """Permet de mettre le programme en pause le temps que l'utilisateur lise les informations."""
        
        print("Appuyez sur la touche 'Echap' pour continuer.")
        keyboard.wait("esc")
        self.flush()
    
    def type_reg(self):
        """Permet de sélectionner quel type de variables seront échangées via le protocole 'Modbus'."""
        
        print("\nQuel type de variables souhaitez vous échanger avec le serveur ?")
        print("- Nombres entiers (int)")
        print("- Nombres à virgule (float)")
        print("- Texte (str)")
        cond = True
        while cond:
            try:
                self.flush()
                self._type_reg = input("Sélectionnez int, float ou string pour continuer : ")
                if self._type_reg == "i" or self._type_reg == "int":
                    self._type_reg = int
                    self._type_reg_str = "int"
                    print("Les valeurs échangées seront désormais interprétées comme des nombres entiers. \n")
                    cond = False
                elif self._type_reg == "f" or self._type_reg == "float":
                    self._type_reg = float
                    self._type_reg_str = "float"
                    print("Les valeurs échangées seront désormais interprétées comme des nombres à virgule. \n")
                    cond = False
                elif self._type_reg == "s" or self._type_reg == "string" or self._type_reg == "str":
                    self._type_reg = str
                    self._type_reg_str = "str"
                    print("Les valeurs échangées seront désormais interprétées comme du texte. \n")
                    cond = False
                else:
                    print("Les données rentrées sont invalides...")
                    
            except KeyboardInterrupt:
                break

    def menu_fb(self):
        """Affiche le menu des différentes fonctions disponibles avec le bus de terrain sélectionné."""
        
        try:
            print("MENU OPERATEUR\n")
            print("Bus en cours d'utilisation : {}.\n".format(self._fieldbus))
            
            self.flush()

            if self._fieldbus == None:
                print("Veuillez terminer la configuration de la passerelle en indiquant le bus de terrain utilisé.")
                self.wait()
                return
            
            else:
                print("Le protocole {} ne dispose pas d'interface, veuillez vérifier les données saisies.".format(self._fieldbus))
                self.wait()
                return
                
        except Exception as e:
            print(e)            

            
    def menu_com(self):
        """Permet d'afficher le menu des différentes fonctions en lien avec le service infonuagique."""
        
        loop = True
        try:
            print("MENU CLOUD\n")
            print("Veuillez choisir une action à effectuer.")
            print("- Options de la base de données.                  (1)")
            print("- Options de synchronisation avec le cloud.       (2)")
            print("- Retour au menu principal.                       (x)")
            
            while loop:
                num = input("Veuillez choisir une option : ")
                
                if num == "1":
                    self.clear()
                    print("Gestion de la base de données...\n")
                    print("- Afficher la base de données.                         (1)")
                    print("- Exporter la base de données dans un fichier csv.     (2)")
                    print("- Réinitialiser la base de données.                    (3)")
                    print("- Retourner au menu principal.                         (x)")
                    
                    while loop:
                        num = input("Veuillez choisir une option : ")
                        
                        if num == "1":
                            print("\nBase de données :")
                            return 11
                        
                        elif num == "2":
                            print("\nExportation des données...")
                            return 12
                        
                        elif num == "3":
                            print("Réinitialisation de la base de données en cours...")
                            return 13
                        
                        elif num == "x":
                            loop = False
                            return num
                            
                        else:
                            print("\nErreur dans la sélection de l'action. Veuillez réessayer.")
                    
                elif num == "2":
                    self.clear()
                    print("Gestion des services infonuagiques...\n")
                    print("- Activer/Désactiver la synchronisation automatique des données avec le Cloud.     (1)")
                    print("- Afficher les données non synchronisées en attente.                               (2)")
                    print("- Synchroniser manuellement les données.                                           (3)")
                    print("- Retourner au menu principal.                                                     (x)")
                    
                    
                    while loop:
                        num = input("Veuillez choisir une option : ")
                        
                        if num == "1":
                            if self._auto_sync:
                                sync = "Activée"
                                word = "désactiver"
                            else:
                                sync = "Désactivée"
                                word = "activer"
                            print("Synchronisation automatique : {}.".format(sync))
                            num = input("Souhaitez vous {} la synchronisation automatique des données (o/n) : ".format(word))
                            if num == "o":
                                self._auto_sync = not self._auto_sync
                                if self._auto_sync:
                                    sync = "Activée"
                                else:
                                    sync = "Désactivée"
                                print("\nSynchronisation automatique : {}.".format(sync))
                                return 21
                            elif num == "n":
                                print("Aucune action effectuée.")
                                return None
                            
                        elif num == "2":
                            print("Données non synchronisées avec le service infonuagique :\n")
                            return 22
                            
                        elif num == "3":
                            print("Synchronisation des données non synchronisées avec le service infonuagique :\n")
                            return 23
                            
                        elif num == "x":
                            loop = False
                            return num
                        
                        else:
                            print("\nErreur dans la sélection de l'action. Veuillez réessayer.")
                    
                elif num == "x":
                    return num
                
                else:
                    print("\nErreur dans la sélection de l'action. Veuillez réessayer.")
            
        except Exception as e:
            print(e)
            
            
        def function_request(self, fct=None):
            pass
        
        def function(self, fct=None, protocol_com=None):
            pass
                

class INTERFACE_CAN(INTERFACE):
    """Adaptateur permettant l'usage du protocole Canbus."""
    
    def __init__(self, canbus, db, fieldbus=None, protocol_com=None, clear=True):
        super().__init__(db, fieldbus, protocol_com, clear)
        self.canbus = canbus
        
    def menu_fb(self):
        """Affiche le menu des différentes fonctions disponibles avec le bus de terrain sélectionné."""
        
        try:
            print("MENU OPERATEUR\n")
            print("Bus en cours d'utilisation : {}.\n".format(self._fieldbus))
            
            self.flush()
                    
            print("- Veuillez choisir une action à effectuer :")
            print("- Envoyer un message.                             (1)")
            print("- Recevoir un message.                            (2)")
            print("- Ecouter le bus et recevoir tous les messages.   (3)")
            print("- Envoyer une requête de contrôle à distance.     (4)")
            print("- Envoyer un message cyclique.                    (5)")
            print("- Accéder aux paramètres de communication.        (6)")
            print("- Retour au menu principal.                       (x)")
            fct = input("Veuillez choisir une option : ")
            return fct
                
        except Exception as e:
            print(e)
        
    def function_request(self, fct):
        """Permet à l'utilisateur de choisir les informations à transmettre à l'instance 'Canbus'."""
        
        try:
            self.flush()        
            if fct == 1:
                print("\nEnvoi d'un message...")
                ID = int(input("ID du message : "))
                data_type = input("Type de données (liste d'octets (1), entier (2), flottant (3), texte (4)) : ")
                
                if data_type == "1":
                    dlc = int(input("Nombre d'octets à transmettre (max 8) : "))
                    if dlc > 8:
                        dlc = 8
                    data = []
                    for i in range(dlc):
                        val = int(input("Veuillez entrer la valeur de l'octet {} ({} restants) : ".format(i, dlc-1-i)))
                        if val >= 0 and val < 256:
                            data.append(val)
                        else:
                            return None
                elif data_type == "2":
                    data = int(input("Valeur de l'entier (il sera codé sur 8 octets) : "))
                elif data_type == "3":
                    data = float(input("Valeur du nombre à virgule : "))
                elif data_type == "4":
                    data = input("Valeur du texte : ")
                else:
                    return None                
                
                return ID, data
            
            elif fct == 2:
                print("\nReception d'un message...")
                timeout = input("Timeout (Appuyer directement sur entrée en laissant ce champ vide si vous ne souhaitez pas avoir de timeout) : ")
                ID = input("ID d'écoute spécifique (Appuyez directement sur entrée en laissant ce champ vide si vous souhaitez écouter toutes les ID) : ")
                save = input("Sauvegarde des données (o/n) : ")
                if timeout == "":
                    timeout = None
                else:
                    timeout = float(timeout)
                if ID == "":
                    ID = None
                else:
                    ID = int(ID)
                if save == "o":
                    save = True
                elif save == "n":
                    save = False
                else:
                    return None
                return timeout, ID, save
            
            elif fct == 3:
                print("\nEcoute du bus...")
                ID = input("ID d'écoute spécifique (Appuyez directement sur entrée en laissant ce champ vide si vous souhaitez écouter toutes les ID) : ")
                save = input("Sauvegarde des données (o/n) : ")
                if ID == "":
                    ID = None
                else:
                    ID = int(ID)
                if save == "o":
                    save = True
                elif save == "n":
                    save = False
                else:
                    return None
                return ID, save
            
            elif fct == 4:
                print("\nEnvoi d'une requête de contrôle à distance...")
                ID = int(input("ID de la requête : "))
                if ID > 0 and ID < 2048:
                    return ID
                else:
                    return None
            
            elif fct == 5:
                print("\nEnvoi d'un message cyclique")
                print("Pour le moment, les seules variables compatibles avec cette fonction sont les listes d'octets.")
                ID = int(input("ID du message : "))
                dlc = int(input("Nombre d'octets à transmettre (max 8) : "))
                if dlc > 8:
                    dlc = 8
                data = []
                for i in range(dlc):
                    val = int(input("Veuillez entrer la valeur de l'octet {} (0 à 255) : ".format(i)))
                    if val >= 0 and val < 256:
                        data.append(val)
                    else:
                        return None
                period = float(input("Délai entre chaque message (en secondes) : "))
                end_time = input("Temps maximal avant l'arrêt de l'émission (laissez ce champ vide si vous ne voulez pas de temps maximal) : ")
                if end_time == "":
                    end_time = None
                else:
                    end_time = int(end_time)
                return ID, data, period, end_time
            
            elif fct == 6:
                print("\nParamètres de communication...")
                print("- Afficher les paramètres de communication   (1).")
                print("- Modifier les paramètres de communication   (2).")
                num = int(input("Veuillez choisir une option : "))
                if num == 1 or num == 2:
                    return num
                else:
                    return None
                
            elif fct == "set_param":
                print("\nQuel paramètre souhaitez vous modifier ?")
                print("- Bitrate                         (1)")
                print("- Chaine                          (2)")
                print("- Type de bus                     (3)")
                print("- Mode d'encodage des flottants   (4)")
                num = int(input("Veuillez choisir une option : "))
                if num in (1,2,3,4):
                    val = input("Veuillez entrer la nouvelle valeur à donner à ce paramètre : ")
                    return num, val
                
                else:
                    return None
            return None
            
        except Exception as e:
            print(e)
        
    def function(self, fct=None, com=None):
        """Recense les différentes fonctions qu'il est possible d'effectuer avec 'Canbus'."""
    
        try:
            request = None
            if fct == "1":
                request = self.function_request(1)
                
                if request:
                    ID, data = request
                    self.canbus.send(ID=ID, data=data)
                    
            elif fct == "2":
                request = self.function_request(2)
                if request:
                    timeout, ID, save = request
                    ans = self.canbus.rcv(timeout=timeout, ID=ID)
                    if ans:
                        result = MESSAGE_CAN(ans)
                        print(result)
                        if save:
                            self.db.add(result)
                            if self._auto_sync:
                                result.sync(com)
                            
            elif fct == "3":
                request = self.function_request(3)
                if request:
                    ID, save = request
                    if save:
                        self.canbus.listen(ID=ID, db=self.db)
                    else:
                        self.canbus.listen(ID=ID, db=None)
                        
            elif fct == "4":
                request = self.function_request(4)
                if request:
                    ID = request
                    self.canbus.remote(ID)
                    
            elif fct == "5":
                request = self.function_request(5)
                if request:
                    ID, data, period, end_time = request
                    self.canbus.send_cyclic(ID=ID, data=data, period=period, end_time=end_time)
                    
            elif fct == "6":
                request = self.function_request(6)
                if request == 1:
                    self.canbus.get_param()
                else:
                    request = self.function_request("set_param")
                    if request:
                        num, val = request
                        if num == 1:
                            self.canbus.set_param(bitrate=int(val))
                        elif num == 2:
                            self.canbus.set_param(channel=val)
                        elif num == 3:
                            self.canbus.set_param(bustype=val)
                        else:
                            self.canbus.set_param(float_mode=val)
                            
            elif fct == "x":
                request = -1
                
            else:
                print("\nErreur dans le choix de l'action à executer.")
            
            if request is None: # Si action_canbus() renvoie None, c'est qu'une erreur s'est produite, il n'y a pas d'action effectuée.
                print("\nAucune action effectuée.")
    
        except Exception as e:
            print(e)
            

class INTERFACE_MOD(INTERFACE):
    """Adaptateur permettant l'usage du protocole Modbus."""
    
    def __init__(self, modbus, db, fieldbus=None, protocol_com=None, clear=True):
        super().__init__(db, fieldbus, protocol_com, clear)
        self.modbus = modbus
        
    def menu_fb(self):
        """Affiche le menu des différentes fonctions disponibles avec le bus de terrain sélectionné."""
        
        try:
            print("MENU OPERATEUR\n")
            print("Bus en cours d'utilisation : {}.\n".format(self._fieldbus))
            
            self.flush()
            
            if self._type_reg == int:
                print("Veuillez choisir une action à effectuer :")
                print("- Lire des coils                                                    (FC1)")
                print("- Lire des entrées discrètes                                        (FC2)") 
                print("- Lire des registres d'exploitation                                 (FC3)")
                print("- Lire des registres d'entrée                                       (FC4)")
                print("- Ecrire dans un coil                                               (FC5)")
                print("- Ecrire dans un registre d'exploitation                            (FC6)")
                print("- Ecrire dans plusieurs coils                                       (FC15)")
                print("- Ecrire dans plusieurs registres d'exploitation                    (FC16)")
                print("- Afficher les paramètres utilisés                                  (param)")
                print("- Choisir l'adresse du serveur (par défaut 1)                       (adresse)")
                print("- Modifier la taille des registres                                  (reg)")
                print("- Changer le type de données traitées (int, float ou string)        (mode)")
                print("- Retour au menu principal.                                         (x)")
                fct = input("Veuillez choisir une option : ")
                return fct
            
            elif self._type_reg == float:
                print("Veuillez choisir une action à effectuer : (Seules les fonctions compatibles avec ce type de variable sont disponibles)")
                print("- Lire des registres d'exploitation                                 (FC3)")
                print("- Lire des registres d'entrée                                       (FC4)")
                print("- Ecrire dans un registre d'exploitation                            (FC6)")
                print("- Ecrire dans plusieurs registres d'exploitation                    (FC16)")
                print("- Afficher les paramètres utilisés                                  (param)")
                print("- Choisir l'adresse du serveur (par défaut 1)                       (adresse)")
                print("- Modifier la taille des registres                                  (reg)")
                print("- Changer le type de données traitées (int, float ou string)        (mode)")
                print("- Retour au menu principal.                                         (x)")
                fct = input("Veuillez choisir une option : ")
                return fct
                
            elif self._type_reg == str:
                print("Veuillez choisir une action à effectuer : (Seules les fonctions compatibles avec ce type de variable sont disponibles)")
                print("- Lire du texte dans les registres d'exploitation                   (FC3)")
                print("- Ecrire du texte dans les registres d'exploitation                 (FC6)")
                print("- Afficher les paramètres utilisés                                  (param)")
                print("- Choisir l'adresse du serveur (par défaut 1)                       (adresse)")
                print("- Modifier la taille des registres                                  (reg)")
                print("- Changer le type de données traitées (int, float ou string)        (mode)")
                print("- Retour au menu principal.                                         (x)")
                fct = input("Veuillez choisir une option : ")
                return fct
                
            else:
                print("Erreur dans les paramètres d'initialisation du menu")
                
        except Exception as e:
            print(e)
    
    def function_request(self, fct):
        """Permet à l'utilisateur de choisir les informations à transmettre à l'instance 'Modbus'."""
        
        try:
            self.flush()
        
            if fct == 1 and self._type_reg == int:
                print("\nLecture de coils...")
                nb = int(input("Nombre de coils à lire : "))
                num = int(input("Adresse du premier coil : "))
                save = input("Sauvegarde des données (o/n) : ")
                if save == "o":
                    save = True
                else:
                    save = None
                return nb, num, save
            
            elif fct == 2 and self._type_reg == int:
                print("\nLecture d'entrées discrètes...")
                nb = int(input("Nombre d'entrées discrètes à lire : "))
                num = int(input("Adresse de la première entrée discrète : "))
                save = input("Sauvegarde des données (o/n) : ")
                if save == "o":
                    save = True
                else:
                    save = None
                return nb, num, save
            
            elif fct == 3:
                print("\nLecture de registres d'exploitation...")
                nb = int(input("Nombre de registres d'exploitation à lire : "))
                num = int(input("Adresse du premier registre d'exploitation : "))
                save = input("Sauvegarde des données (o/n) : ")
                if save == "o":
                    save = True
                else:
                    save = None
                return nb, num, self._type_reg, save
            
            elif fct == 4 and self._type_reg != str:
                print("\nLecture de registres d'entrée...")
                nb = int(input("Nombre de registres d'entrée à lire : "))
                num = int(input("Adresse du premier registre d'entrée : "))
                save = input("Sauvegarde des données (o/n) : ")
                if save == "o":
                    save = True
                else:
                    save = None
                return nb, num, self._type_reg, save
            
            elif fct == 5 and self._type_reg == int:
                print("\nEcriture d'un coil...")
                num = int(input("Adresse du coil  : "))
                val = int(input("Nouvelle valeur du coil (0 ou 1) : "))
                if val not in [0, 1]:
                    print("Les données saisies ne sont pas valides")
                    return None
                return num, val
            
            elif fct == 6:
                print("\nEcriture d'un registre d'exploitation...")
                print("Attention : La passerelle est actuellement configurée pour envoyer des données de type {}.".format(self._type_reg_str))
                num = int(input("Adresse du registre d'exploitation à modifier : "))
                val = input("Nouvelle valeur : ")
                if self._type_reg == int:
                    val = int(val)
                elif self._type_reg == float:
                    val = float(val)
                return num, val, self._type_reg
            
            elif fct == 15 and self._type_reg == int:
                print("\nEcriture de plusieurs coils...")
                nb = int(input("Nombre de coils à modifier : "))
                num = int(input("Adresse du premier coil à modifier : "))
                print("Entrez les valeurs à donner aux coils (0 ou 1) : ")
                val = [0]*nb
                for k in range(nb):
                    if nb-k != 1:
                        print(str(nb-k) + " valeurs restantes")
                    else:
                        print(str(nb-k) + " valeur restante")
                    val[k] = int(input())
                    if val[k] not in [0, 1]:
                        print("Les données saisies ne sont pas valides")
                        return None
                return num, val
            
            elif fct == 16 and self._type_reg != str:
                print("\nEcriture de plusieurs registres d'exploitation...")
                nb = int(input("Nombre de registres d'exploitation à modifier : "))
                num = int(input("Adresse du premier registre d'exploitation à modifier : "))
                print("Valeurs à donner aux registres d'exploitations ({}) : ".format(str(self._type_reg_str)))
                val = [0]*nb
                if self._type_reg == int:
                    for k in range(nb):
                        if nb-k != 1:
                            print(str(nb-k) + " valeurs restantes")
                        else:
                            print(str(nb-k) + " valeur restante")
                        val[k] = int(input())
                else :
                    for k in range(nb):
                        if nb-k != 1:
                            print(str(nb-k) + " valeurs restantes")
                        else:
                            print(str(nb-k) + " valeur restante")

                        val[k] = float(input())
                return nb, num, val, self._type_reg
            
            elif fct == "adresse":
                print("\nChangement de l'adresse du noeud...")
                address = int(input("Nouvelle adresse de communication : "))
                if address > 0:
                    return address
            
            elif fct == "mode":
                print("\nChangement du type de registres utilisé...")
                self.type_reg()
                
            elif fct == "param":
                print("\nParamètres de communication...")
                print("- Afficher les paramètres de communication   (1).")
                print("- Modifier les paramètres de communication   (2).")
                num = int(input("Veuillez choisir une option : "))
                if num == 1 or num == 2:
                    return num
                else:
                    return None
                
            elif fct == "reg":
                print("\nModification des registres")
                reg_int_address = int(input("Adresse du premier registre d'exploitation dédié aux int   : "))
                reg_float_address = int(input("Adresse du premier registre d'exploitation dédié aux float : "))
                reg_text_address = int(input("Adresse du premier registre d'exploitation dédié au texte  : "))
                reg_text_size = int(input("Nombre de registres dédiés au texte : "))
                req = [reg_int_address, reg_float_address, reg_text_address, reg_text_size]
                return req
                
            elif fct == "set_param":
                print("\nQuel paramètre souhaitez vous modifier ?")
                print("- Baudrate                        (1)")
                print("- Port                            (2)")
                print("- Adresse                         (3)")
                print("- Mode d'encodage des flottants   (4)")
                num = int(input("Veuillez choisir une option : "))
                if num in (1,2,3,4):
                    val = input("Veuillez entrer la nouvelle valeur à donner à ce paramètre : ")
                    return num, val
                
            elif fct == "sleep":
                while True:
                    self.flush()
                    val = input("Si vous souhaitez apporter une modification à cette fonctionnalité, veuillez rentrer 0 ou 1, sinon laissez le champ vide : ")
                    if val == "0":
                        print("La fonctionnalité de réveil sera maintenant désactivée.")
                        return False
                    elif val == "1":
                        print("La fonctionnalité de réveil sera maintenant activée.")
                        return True
                    elif val == "":
                        return
                    else:
                        print("Les données saisies sont invalides.")            
            
            return None
                    
        except Exception as e:
            print(e)
    
    def function(self, fct=None, com=None):
        """Recense les différentes fonctions qu'il est possible d'effectuer avec 'Modbus'."""
    
        try:
            request = None
            if fct == "1" or fct == "FC1":
                request = self.function_request(1)
                if request:
                    nb, num, save = request
                    ans = self.modbus.FC1(nb, num)
                    if ans:
                        result = MESSAGE_MOD(ans)
                        print(result)
                        if save:
                            self.db.add(result)
                            if self._auto_sync:
                                result.sync(com)
                        
            elif fct == "2" or fct == "FC2":
                request = self.function_request(2)
                if request:
                    nb, num, save = request
                    ans = self.modbus.FC2(nb, num)
                    if ans:
                        result = MESSAGE_MOD(ans)
                        print(result)
                        if save:
                            self.db.add(result)
                            if self._auto_sync:
                                result.sync(com)
                        
            elif fct == "3" or fct == "FC3":
                request = self.function_request(3)
                if request:
                    nb, num, reg, save = request
                    ans = self.modbus.FC3(nb, num, reg)
                    if ans:
                        result = MESSAGE_MOD(ans)
                        print(result)
                        if save:
                            self.db.add(result)
                            if self._auto_sync:
                                result.sync(com)
                    
            elif fct == "4" or fct == "FC4":
                request = self.function_request(4)
                if request:
                    nb, num, reg, save = request
                    ans = self.modbus.FC4(nb, num, reg)
                    if ans:
                        result = MESSAGE_MOD(ans)
                        print(result)
                        if save:
                            self.db.add(result)
                            if self._auto_sync:
                                result.sync(com)
                        
            elif fct == "5" or fct == "FC5":
                request = self.function_request(5)
                if request:
                    num, val = request
                    self.modbus.FC5(num, val)
                    
            elif fct == "6" or fct == "FC6":
                request = self.function_request(6)
                if request:
                    num, val, reg = request
                    self.modbus.FC6(num, val, reg)
                    
            elif fct == "15" or fct == "FC15":
                request = self.function_request(15)
                if request:
                    num, val = request
                    self.modbus.FC15(num, val)
                    
            elif fct == "16" or fct == "FC16":
                request = self.function_request(16)
                if request:
                    nb, num, val, reg = request
                    self.modbus.FC16(nb, num, val, reg)

                    
            elif fct == "param":
                request = self.function_request("param")
                if request == 1:
                    self.modbus.get_param()
                else:
                    request = self.function_request("set_param")
                    if request:
                        num, val = request
                        if num == 1:
                            self.modbus.set_param(baudrate=int(val))
                        elif num == 2:
                            self.modbus.set_param(port=val)
                        elif num == 3:
                            self.modbus.set_param(address=val)
                        else:
                            self.modbus.set_param(float_mode=val)
            
            elif fct == "adresse":
                request = self.function_request("adresse")
                if request:
                     self.modbus.set_param(address=request)
                     
            elif fct == "reg":
                self.modbus.get_reg()
                request = self.function_request("reg")
                if request:
                    reg_int_address, reg_float_address, reg_text_address, reg_text_size = request
                    reg_int_size = reg_float_address - reg_int_address
                    reg_float_size = reg_text_address - reg_float_address
                    self.modbus.set_reg(reg_int_address, reg_int_size, reg_float_address, reg_float_size, reg_text_address, reg_text_size)
                    
            
            elif fct == "mode":
                self.function_request("mode")
                
            elif fct == "sleep":
                if self.modbus._sleeping_on:
                    print("La fonctionnalité de réveil est actuellement activée.")
                else:
                    print("La fonctionnalité de réveil est actuellement désactivée.")
                request = self.function_request("sleep")
                            
            elif fct == "x":
                request = fct
                
            else:
                print("\nErreur dans le choix de l'action à executer.")
            
            if request is None: # Si function_request() renvoie None, c'est qu'on a choisi cela pour indiquer qu'aucune action n'avait été effectuée.
                print("Aucune action effectuée")
    
        except Exception as e:
            print(e)

