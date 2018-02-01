def check_ruc_private(self, ruc):
    """
    Aloritmo para verificar RUC de Empresa Privada.
    """
    try:
        if (int(ruc[0] + ruc[1])) < 23:
            prueba1 = True
        else:
            prueba1 = False

        if int(ruc[2]) == 9:
            prueba2 = True
        else:
            prueba2 = False

        val0 = int(ruc[0]) * 4
        val1 = int(ruc[1]) * 3
        val2 = int(ruc[2]) * 2
        val3 = int(ruc[3]) * 7
        val4 = int(ruc[4]) * 6
        val5 = int(ruc[5]) * 5
        val6 = int(ruc[6]) * 4
        val7 = int(ruc[7]) * 3
        val8 = int(ruc[8]) * 2

        tot = val0 + val1 + val2 + val3 + val4 + val5 + val6 + val7 + val8
        veri = tot - ((tot / 11)) * 11

        if veri == 0:
            if (int(ruc[9])) == 0:
                prueba3 = True
            else:
                prueba3 = False
        else:
            if (int(ruc[9])) == (11 - veri):
                prueba3 = True
            else:
                prueba3 = False

        if (int(ruc[10])) + (int(ruc[11])) + (int(ruc[12])) > 0:
            prueba4 = True
        else:
            prueba4 = False

        if prueba1 and prueba2 and prueba3 and prueba4:
            return True
        else:
            return False
    except:
        return False


def check_ruc_government(self, ruc):
    """
    Verificar RUC de Empresas Publicas
    """
    try:
        if (int(ruc[0] + ruc[1])) < 23:
            prueba1 = True
        else:
            prueba1 = False

        if int(ruc[2]) == 6:
            prueba2 = True
        else:
            prueba2 = False

        val0 = int(ruc[0]) * 3
        val1 = int(ruc[1]) * 2
        val2 = int(ruc[2]) * 7
        val3 = int(ruc[3]) * 6
        val4 = int(ruc[4]) * 5
        val5 = int(ruc[5]) * 4
        val6 = int(ruc[6]) * 3
        val7 = int(ruc[7]) * 2

        tot = val0 + val1 + val2 + val3 + val4 + val5 + val6 + val7
        veri = tot - ((tot / 11)) * 11

        if veri == 0:
            if (int(ruc[8])) == 0:
                prueba3 = True
            else:
                prueba3 = False
        else:
            if (int(ruc[8])) == (11 - veri):
                prueba3 = True
            else:
                prueba3 = False

        if (int(ruc[9])) + (int(ruc[10])) + (int(ruc[11])) + (int(ruc[12])) > 0:
            prueba4 = True
        else:
            prueba4 = False

        if prueba1 and prueba2 and prueba3 and prueba4:
            return True
        else:
            return False
    except:
        return False


def check_ruc_individual(self, ruc):
    """
    Verificar RUC de Persona Natural
    """
    try:
        if (int(ruc[0] + ruc[1])) < 23:
            prueba1 = True
        else:
            prueba1 = False

        if (int(ruc[2]) < 6):
            prueba2 = True
        else:
            prueba2 = False

        valores = [int(ruc[x]) * (2 - x % 2) for x in range(9)]
        suma = sum(map(lambda x: x > 9 and x - 9 or x, valores))
        veri = 10 - (suma - (10 * (suma / 10)))
        if int(ruc[9]) == int(str(veri)[-1:]):
            prueba3 = True
        else:
            prueba3 = False

        if ((int(ruc[10])) + (int(ruc[11])) + (int(ruc[12])) > 0):
            prueba4 = True
        else:
            prueba4 = False

        if (prueba1 and prueba2 and prueba3 and prueba4):
            return True
        else:
            return False
    except:
        return False


def check_id_document(self, ced):
    """
    Verificar Cedula
    """
    try:
        valores = [int(ced[x]) * (2 - x % 2) for x in range(9)]
        suma = sum(map(lambda x: x > 9 and x - 9 or x, valores))
        veri = 10 - (suma - (10 * (suma / 10)))
        if int(ced[9]) == int(str(veri)[-1:]):
            return True
        else:
            return False
    except:
        return False