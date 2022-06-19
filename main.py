#Langue supportée : Français
#Licence : CC BY-NC-ND 2.5 CA

from ressources import * 

def menu_home(num):
    """Permet de mettre en lien les différentes instances de la passerelle au sein de l'interface utilisateur."""

    try:
        interface.clear()

        if num == "x":
            print("Fermeture du programme...")
            if canbus.is_open:
                canbus.shutdown()
            if modbus.is_open:
                modbus.shutdown()
            time.sleep(1)
            interface.clear()
            exit()
            
        elif num == "1":
            while True:
                fct, val = interface.menu_config()
                if fct == "bus":
                    return val
                elif fct == "sleep":
                    is_on = interface.function(fct=fct)
                    modbus.sleep(is_on)
                elif fct == "com":
                    if interface._protocol_com == "mqtt":      
                        com.select(mqtt_ts)
                    elif interface._protocol_com == "rest":
                        com.select(rest_ts)
                
                if fct != "x":
                    interface.wait()
                    interface.clear()
                
                else:
                    return
            
        elif num == "2":
            while True:
                if interface._fieldbus == "modbus":
                    if not modbus.is_open:
                        print("L'instance Modbus n'a pas été correctement initialisée, veuillez vérifier les paramètres.")
                        interface.wait()
                        interface.clear()
                        return
                elif interface._fieldbus == "canbus":
                    if not canbus.is_open:
                        print("L'instance Canbus n'a pas été correctement initialisée, veuillez vérifier les paramètres.")
                        interface.wait()
                        interface.clear()
                        return

                fct = interface.menu_fb()
                interface.function(fct=fct, com=com.protocol)
                    
                if fct != "x":
                    interface.wait()
                    interface.clear()
                    
                else:
                    return
                
        elif num == "3":
            while True:
                fct = interface.menu_com()
                db.function(fct=fct, protocol_com=com.protocol)

                if fct != "x":
                    interface.wait()
                    interface.clear()
                    
                else:
                    return
            
            
    except Exception as e:
        print(e)

# Boucle principale du programme
if __name__ == "__main__":
    run = True
    while run:
        num = interface.home()
        bus = menu_home(num)
        if bus:
            if bus == "modbus":
                interface = INTERFACE_MOD(modbus, db, fieldbus="modbus", protocol_com=com.name)

            elif bus == "canbus":
                interface = INTERFACE_CAN(canbus, db, fieldbus="canbus", protocol_com=com.name)
            else:
                interface = INTERFACE(fieldbus=bus, protocol_com=com.name)

        interface.clear()