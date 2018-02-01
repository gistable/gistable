#!/usr/bin/env python
#-*- coding:utf-8 -*-

from __future__ import division
import numpy as np
from pylab import *
import matplotlib.pyplot as plt
import seaborn as sns
import prettyplotlib as ppl

sns.set(style="ticks", palette="Set2")
sns.despine()

%matplotlib inline 

pi_hat = []
nn = 1 # numero de veces que repetimos la simulación

for i in np.arange(nn):

	n = 10000000 # número de valores aleatorios
	u = np.random.uniform(0,1,n) # valores aleatorios de un eje
	v = np.random.uniform(0,1,n) # valores aleatorios del otro eje
	dis = np.sqrt((u-0.5) ** 2 + (v-0.5) ** 2) # distancia al centro
	dis_i = filter(lambda x: x < 0.5, dis) # filtramos los que cumplen la condición de círculo
	o = len(dis_i) / n # calculamos el área del círculo
	pi = o * 4 # aplicamos la ecuación de pi
	pi_hat += [pi] # guardamo la estimación de pi de cada simulación

print "Pi_hat = ", np.mean(pi_hat) # mostramos el valor medio de pi para las nn estimaciones 
print "Pi real = 3.14159265359" # el valor real de pi
print "ECM =", np.mean(np.subtract(3.14159265359,pi_hat) ** 2)

# Funciones auxiliares para el grafico
# necesitamos solo los valores aleatorios que cumplen la condicion de circunferencia
u_f = [] 
v_f = []

for i,e in enumerate(u):
    if np.sqrt((u[i]-0.5 )** 2 + (v[i]-0.5) ** 2) < 0.5:
        u_f += [u[i]]
        v_f += [v[i]]

plt.figure(figsize=(6,12))

ax1 = subplot(211) # gráfico de la simulación de montercarlo
ax1.axhline(0.5, color="grey", alpha=0.5)
ax1.axvline(0.5, color="grey", alpha=0.5)
ax1.set_title(u"Simulación Montecarlo", fontsize=14)
ppl.scatter(u,v)
ppl.scatter(u_f,v_f, linewidth=0.08)

ax2 = subplot(212) # gráfico de las nn estimaciones de pi
ppl.scatter(range(len(pi_hat)),pi_hat)
ax2.axhline(3.14159265359, color="grey", alpha=0.5, linewidth=2)
text(len(pi_hat)*1.01, 3.14159265359, "Pi = 3.1415...")
ax2.set_title(u"Estimación de Pi", fontsize=14)

# plt.show() # quitar el \"#" si usas el shell
#plt.savefig("simulacion_pi_montercalo.png", dpi=200) # quitar el \# para guardar la imagen.