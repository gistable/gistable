class Pessoa:
    def _setNome(self,nome):
        print("Registrando nome.")
        self._nome = nome
    def _getNome(self):
        print("Recuperando nome.")
        return self._nome
    def _delNome(self):
        print("Apagando o nome")
        del self._nome
    nome = property(_getNome,_setNome,_delNome,"Propriedade Nome ") 
p = Pessoa()
p.nome = "Raimundo dos Santos Pereira"
print("Pessoa = ",p.nome)
del p.nome