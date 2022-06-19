import struct

def from_list(list_val):
    """Permet d'extraire un entier à partir d'une liste d'entiers contenus dans 8 octets."""
    
    try:
        val = 0
        for b in list_val:
            val = val * 256 + int(b)
            
        return val

    except Exception as e:
        print(e)


def to_list(val):
    """Permet d'écrire un entier sur une liste d'entiers contenus dans 8 octets."""
    
    try:
        if val > (2**64 - 1): # C'est le plus grand int obtenable à partir de 8 octets.
            print("Erreur, le nombre est trop grand pour être codé sur 8 octets.")
            return -1
        list_val = []
        for i in range(8):
            list_val.append(val >> (i*8) & 0xff)
        list_val.reverse()
        return list_val

    except Exception as e:
        print(e)

def float_decode(mode, data, scale=0.01, offset=0):
    """
    Permet la conversion d'un nombre entier codé sur 8 octets en un nombre flottant.
    Méthode des valeurs fractionnaires : mode="frac"
    Méthode Binary32 conformément à la norme IEEE-754 : mode="binary32"
    """
    
    try:
        val = from_list(data)
        
        if mode == "frac":
            result = val * scale + offset
            return result
        
        elif mode == "bin32":
            return bin32(data)
        
        else:
            print("Erreur, ce mode n'est pas défini.")
    
    except Exception as e:
        print(e)
        
def float_encode(mode, data, scale=0.01, offset=0):
    """
    Permet la conversion d'un flottant en un nombre entier codé sur 8 octets.
    Méthode des valeurs fractionnaires : mode="frac"
    Méthode Binary32 conformément à la norme IEEE-754 : mode="binary32"
    """
    
    try:
        assert isinstance(data, float)
        
        if mode == "frac":
            print((data - offset)/scale)
            val = int((data - offset)/scale)
            return to_list(val)
        
        elif mode == "bin32":
            return bin32(data)
        
        else:
            print("Erreur, ce mode d'encodage n'est pas défini.")
            return -1
        
    except Exception as e:
        print(e)
        
        
def float_to_bin(num):
    """Permet d'écrire un nombre à virgule sous sa représentation binaire, en 32 bits."""
    
    try:
        bits = struct.unpack('!I', struct.pack('!f', num))[0] # !I = Unsigned int et !f = float
        return "{:032b}".format(bits)
    
    except Exception as e:
        print(e)

def int_to_bin(num):
    """Permet d'écrire un nombre entier sous sa représentation binaire, en 8 bits."""
    
    try:
        return "{:08b}".format(num)
    
    except Exception as e:
        print(e)

def bytes_join(list_int):
    """Permet d'écrire une liste d'entier sous forme binaire en les juxstaposant les uns aux autres."""
    
    try:
        result = ""
        for val in list_int:
            result += int_to_bin(val)
        return result
    
    except Exception as e:
        print(e)

def frame8_split(frame):
    """Permet de séparer une frame de 8 octets en 2 frames de 4 octets et d'isoler ainsi les flottants (32 bits) contenus dans cette dernière."""
    
    try:
        assert isinstance(frame, list)
        assert len(frame) == 8
        
        val1 = frame[:4]
        val2 = frame[4:]
        return val1, val2
    
    except AssertionError:
        print("Les paramètres d'entrée ne sont pas valides.")
        return -1, -1

def bin32(data):
    """ Cette fonction contient l'algorithme de conversion des nombres flottants de la norme IEEE754.
        Si l'entrée est un flottant, la liste des entiers le représentant sera renvoyée, et inversement si c'est la liste qui est donnée en entrée.
    """
    
    try:
        assert isinstance(data, (str, float, list, int))
        mode = "decode"
        
        # Extraction des données
        if isinstance(data, float):
            mode = "encode"
        
        if mode == "decode":
            
            if isinstance(data, int):
                data = int_to_bin(data)
                
            if isinstance(data, list):
                
                for val in data:
                    assert isinstance(val, int)
                    
                if len(data) == 8:
                    data1, data2 = frame8_split(data)
                    data1 = bytes_join(data1)
                    data2 = bytes_join(data2)
                    
                    if int(data2, base=2) != 0:
                        data = data2
                        
                    elif int(data1, base=2) != 0:
                        data = data1
                        
                    else:
                        data = "0"*32
                        
                else:
                    data = "0"*32
                
            if isinstance(data, str):
                str_sgn = data[0]
                str_exp = data[1:9]
                str_mant = data[9:]
            
            # Interprétation des données
            sgn = (-1) ** int(str_sgn)
            mant = 0
            
            if int(str_exp, base=2) != 0: #Cas classique, il est rare que l'exponent brut ne contienne que des 0.
                exp = 2**(int(str_exp, base=2) - 127)
                str_mant = "1" + str_mant
                for i in range(len(str_mant)):
                    mant += int(str_mant[i])/(2**(i))
                
            else: # Cas d'un overflow
                exp = 2**(-126)
                for i in range(len(str_mant)):
                    mant += int(str_mant[i])/(2**(i+1))
                    
            return sgn * exp * mant
        
        else: #On a un float en entrée et on veut le convertir.
            
            bits = float_to_bin(data)
            uint = int(bits, base=2)
            frame = to_list(uint)
            return frame             
            
            
    except AssertionError:
        print("Les paramètres d'entrées ne sont pas valides, vérifiez que la liste de données ne contient que des entiers.")
        
    except Exception as e:
        print(e)

def text_to_int(text):
    """Permet de retourner une liste de nombres entiers représentant chacun un caractère du texte d'entrée."""
    
    try:
        assert isinstance(text, str)

        list_int = []
        for i in range(len(text)):
            list_int.append(ord(text[i]))
        return(list_int)
        
    except AssertionError:
        print("Les paramètres d'entrée ne sont pas valides.")
        
    except Exception as e:
        print(e)
        
def int_to_text(list_int):
    """Permet de retourner le texte que représente la liste d'entiers donnée en entrée."""
    
    try:
        assert isinstance(list_int, list)
        
        text = ""
        for i in range(len(list_int)):
            text += chr(list_int[i])
        return text
        
    except AssertionError:
        print("Les paramètres d'entrée ne sont pas valides.")
        
    except Exception as e:
        print(e)

def text_split(text, lenght=8):
    """Permet de diviser une chaine de caractère en plusieurs chaines de caractères ayant une longueur maximale définie."""
    
    try:
        return [text[i:i+lenght] for i in range(0, len(text), lenght)]
    
    except Exception as e:
        print(e)