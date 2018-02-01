'''
Modelo de Rede Neural Artificial
Por: Nathan de Lima Silva
'''

import numpy;

class Neuronio:
	def __init__(self, n): #n = numero de entradas
		self.n = n;
		self.w = numpy.zeros(n);
		self.setBias(1);
		self.setWeight(numpy.ones(n));

	def setBias(self, b):
		self.b = b;
	
	def setWeight(self, w):
		for k in range(0, self.n):
			self.w[k] = w[k];

	def setInputs(self, x):
		self.x = x;

	#Função de ativação do perceptron.
	def f(self, g):
		return g; #Função linear neste caso.

	def getOutput(self):
		g = 0;
		for k in range(0, self.n):
			g = g+self.w[k]*self.x[k];
		g = g+self.b;
		return self.f(g);


class Camada:
	def __init__(self, Nneuronios, Nentradas):
		self.neuronio=[];
		for count in range(0, Nneuronios, 1):
			self.neuronio.append(Neuronio(Nentradas));


class RNA:

	def __init__(self, Dim):
		self.Dim = Dim;
		self.Ncamadas = len(Dim)-1; #Sintaxe: {numero de entradas da rede, {numero de neuronio camadas 1:N}}
		self.camada = [];
		for k in range(0, self.Ncamadas, 1):
			self.camada.append(Camada(Dim[k+1], Dim[k]));

	def getOutput(self, x):
		self.x = x
		y=0;
		for m in range(0, self.Ncamadas, 1):
			y = numpy.zeros(self.Dim[m+1]);
			#print(x)
			for k in range(0, self.Dim[m+1]):
				self.camada[m].neuronio[k].setInputs(self.x);
				y[k] = self.camada[m].neuronio[k].getOutput();
			self.x = y
		return y;


Dim = [4, 2, 2, 2];
rede = RNA(Dim)

print(rede.getOutput([0, 0, 0, 0]))