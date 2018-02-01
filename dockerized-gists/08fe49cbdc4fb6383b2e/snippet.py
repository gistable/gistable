import matplotlib.pyplot as plt
import pandas as pd

A=[5,0,0,0,0,0,6]
B=[0,1,2,0,0,4,0]
C=[0,0,0,4,2,0,0]
D=[0,5,6,4,2,2,0]
E=[0,1,2,3,4,5,6]

fig = plt.gcf()
fig.set_size_inches(6.6,4.4)
#fig.set_dpi=20

p1 = plt.bar(E,A, align='center', color='gray', edgecolor ='none')
p2 = plt.bar(E,B, align='center', color='blue', bottom=D, edgecolor ='none')
p3 = plt.bar(E,C, align='center', color='red', bottom=D, edgecolor ='none')
plt.figure(figsize=(1,1111))
plt.show()

Utilidad = pd.read_excel('utilidad.xls','utilidad')
Utilidad = Utilidad.T
