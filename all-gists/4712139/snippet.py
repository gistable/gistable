def Mayuscula(String):
    String = String.upper()
    return String
def Minuscula(String):
    String = String.lower()
    return String
def reverse(s):
    result = ""
    for c in s:
        if(c.isupper() == 1 ):
        # Si la letra es minúscula entonces se convierte en mayúscula
            result = Minuscula(c)+result
        else:
        # Si es mayúscula la vuelve minuscula
            result = Mayuscula(c)+result
    return result
    
t = input("Por favor, introduzca una cadena: ")
print ("El inverso de ", t, "es ", reverse(call))