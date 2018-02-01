# -*- coding: iso-8859-15 -*-
"""
Behavior Tree Example
"""


class WorldStatus(object):
    def __init__(self):
        self.aperta = False  # Porta aperta?
        self.step = 3        # Distanza dalla porta


class Task(object):
    """
    Classe base per un nodo di un Behavior Tree
    """
    def __init__(self):
        self._children = []

    def run(self):
        pass

    def add_child(self, c):
        self._children.append(c)


class Selector(Task):
    """
    Implementazione di un Selector
    """
    def __init__(self):
        super(Selector, self).__init__()

    def run(self):
        for c in self._children:
            if c.run():
                return True
        return False


class Sequence(Task):
    """
    Implementazione di un Sequence
    """
    def __init__(self):
        super(Sequence, self).__init__()

    def run(self):
        for c in self._children:
            if not c.run():
                return False
        return True


class PortaAperta(Task):
    def __init__(self, status):
        super(PortaAperta, self).__init__()
        self._status = status

    def run(self):
        if self._status.aperta:
            print("La Porta è aperta")
        else:
            print("La Porta è chiusa!")
        return self._status.aperta


class Avvicinati(Task):
    def __init__(self, status):
        super(Avvicinati, self).__init__()
        self._status = status

    def run(self):
        if self._status.step > 0:
            print("Mi avvicino!")
            self._status.step -= 1
            return True
        return False


class Apri(Task):
    def __init__(self, status):
        super(Apri, self).__init__()
        self._status = status

    def run(self):
        if self._status.step != 0:
            print("Ancora troppo lontano!")
            return False
        print("Apro la porta!")
        self._status.aperta = True
        return True


# MAIN #
def main():
    # Definisco i nodi funzionali
    root = Sequence()
    seq = Sequence()
    sel = Selector()

    # Creo lo stato del mondo
    status = WorldStatus()

    # Creo le azioni
    checkaperta = PortaAperta(status)
    avvicinati = Avvicinati(status)
    apri = Apri(status)

    # Assemblo l'albero
    root.add_child(sel)

    sel.add_child(checkaperta)
    sel.add_child(seq)

    seq.add_child(avvicinati)
    seq.add_child(apri)

    # Eseguo la radice finché non ritorna vero
    while not root.run():
        print("---")
