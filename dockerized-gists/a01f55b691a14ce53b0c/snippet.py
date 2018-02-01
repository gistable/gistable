import unittest


class SacarUsecase(object):
    def __init__(self):
        self.notas = []
        self.valor = 0

    def execute(self, valor):
        self.valor = valor

        self._pegar_nota(100)
        self._pegar_nota(50)
        self._pegar_nota(20)
        self._pegar_nota(10)

        return self.notas

    def _pegar_nota(self, nota):
        while (self.valor - nota) >= 0:
            self.notas.append(nota)
            self.valor -= nota


class Tests(unittest.TestCase):
    def setUp(self):
        self.usecase = SacarUsecase()

    def test_sacar_10(self):
        notas = self.usecase.execute(10)

        self.assertEqual([10], notas)

    def test_sacar_20(self):
        notas = self.usecase.execute(20)

        self.assertEqual([20], notas)

    def test_sacar_30(self):
        notas = self.usecase.execute(30)

        self.assertEqual([20, 10], notas)

    def test_sacar_40(self):
        notas = self.usecase.execute(40)

        self.assertEqual([20, 20], notas)

    def test_sacar_50(self):
        notas = self.usecase.execute(50)

        self.assertEqual([50], notas)

    def test_sacar_80(self):
        notas = self.usecase.execute(80)

        self.assertEqual([50, 20, 10], notas)

    def test_sacar_90(self):
        notas = self.usecase.execute(90)

        self.assertEqual([50, 20, 20], notas)

    def test_sacar_100(self):
        notas = self.usecase.execute(100)

        self.assertEqual([100], notas)

    def test_sacar_200(self):
        notas = self.usecase.execute(200)

        self.assertEqual([100, 100], notas)


if __name__ == '__main__':
    unittest.main()
