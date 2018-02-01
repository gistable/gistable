import numpy as np
import random


class Node:
	def __init__(self,t,L,R,D,S,V,M,X):
		self.t=t  
		self.L=L
		self.R=R
		self.D=D
		self.S=S
		self.V=V
		self.M=M
                self.X=X

#t Index of Node
#L Index of Left child
#R Index of right child
#D Depth of the Node
#S Value of split
#V Feature of split
#M Subset array
#X Execution Flag


########################################################################################

def Build(Tr):

#	print len(Tr.M)

	Tr.S=maxgini[0,1]

	Tr.V=maxgini[0,0]

        Tr.X=1
        #Flag of the Node is building

	#Split condition

	Tr.L=2*Tr.t+1
	Tree.append(Node(Tr.L,"L","R",Tr.D+1,"S","V",Tr.M[Tr.M[:,Tr.V]<Tr.S],"X"))

	Tr.R=2*Tr.t+2
	Tree.append(Node(Tr.R,"L","R",Tr.D+1,"S","V",Tr.M[Tr.M[:,Tr.V]>Tr.S],"X"))

#########################################################################################
##Main function##########################################################################
def TT(depth):

	temp=[]

	for index,node in enumerate(Tree):
		 temp.append(Tree[index].D)

#Expand tree, using last node to compute split

	for index,node in enumerate(Tree):

#Depth condition
		if (node.D==temp[-1] and node.D<=depth):
			if node.X<>1:
				if len(Tree[index].M)>1:
					ginisplit(Tree[index].M)
					if sum(maxgini[:,2]) > 0 :
					
						Build(Tree[index])
						TT(depth)


##########################################################################################

def split(v,a):

	global Temp1

	sp=np.sort(np.unique(a[:,v]))

	Temp1=np.zeros([len(sp)-1, 3])

	#If no split because one unique value on data, avoid nan error for mean calculus
	if len(sp)==1:
		return

	for i in range(len(sp)-1):

		####Root
		c=np.bincount(a[:,0])
		cs=len(a)

		if len(c)==1:
			Iroot=1-(float(c[0])/cs)**2
		else:
			Iroot=1-(float(c[0])/cs)**2-(float(c[1])/cs)**2

		####Left
		l1=a[a[:,v] < np.mean(sp[i:i+2])]
		l2=np.bincount(l1[:,0])

		ls=len(l1)

		if len(l2)==1:
			Il=1-(float(l2[0])/ls)**2
		else:
			Il=1-(float(l2[0])/ls)**2-(float(l2[1])/ls)**2


		####Right
		r1=a[a[:,v] > np.mean(sp[i:i+2])]
		r2=np.bincount(r1[:,0])

		rs=len(r1)

		if len(r2)==1:
			Ir=1-(float(r2[0])/rs)**2
		else:
			Ir=1-(float(r2[0])/rs)**2-(float(r2[1])/rs)**2


		#################################################
		#Impurity Gin gain like R
		I=(Iroot-(float(ls)/cs)*Il-(float(rs)/cs)*Ir)*cs

		#Find maximum
		Temp1[i,0]=v
		Temp1[i,1]=np.mean(sp[i:i+2])
		Temp1[i,2]=I


	Temp1=Temp1[Temp1[:,2]==Temp1[:,2].max()]

#######################################################################
def ginisplit(matrix):

	global maxgini

	maxgini=np.reshape([], (0,3))
	#target exclusion

	for i in range(1,matrix.shape[1]):

		split(i,matrix)
		maxgini=np.append(maxgini, Temp1,axis=0)

	maxgini=maxgini[maxgini[:,2]==maxgini[:,2].max()]
	if sum(maxgini[:,2]) == 0 :
		return
#	print maxgini

#########################################################################
##Test Array    #########################################################

np.random.seed(42)

X=np.random.randint(10, size=(100, 4))

Y=np.random.randint(2, size=100)

a=np.column_stack((Y,X))

##########################################################################


Tree=[]


Tree.append(Node(0,"L","R",0,"S","V",a,"X"))

TT(2)

##Tree structure#########################################################

for index,node in enumerate(Tree):
	print index,node.t,"*",node.L,node.R,"*","Depth:",node.D,node.S,len(node.M)