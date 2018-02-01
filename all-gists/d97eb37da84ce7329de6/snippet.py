from fipy import Grid1D, CellVariable, FaceVariable, TransientTerm, DiffusionTerm, ExponentialConvectionTerm, ImplicitSourceTerm, Viewer
import matplotlib.pyplot as plt
import numpy as np

L = 10.0
nx = 100
dx = L/nx
timeStep = dx/10.0

steps = 150
phim = 0.10   # mobile zone porosity
phiim = 0.05  # immobile zone porosity
beta = 0.05    # mobile/immobile domain transfer rate
D = 1.0E-1    # mobile domain diffusion coeff
Rm = 1.0     # mobile domain retardation coefficient
Rim = 1.0    # immobile domain retardation coefficient

betaT = phiim*Rim/(phim*Rm)
DR = D/Rm

m = Grid1D(dx=dx, nx=nx)
c0 = np.zeros(nx, 'd')
c0[20:50] = 1.0

# mobile domain concentration
cm = CellVariable(name="$c_m$", mesh=m, value=c0)

# immobile domain concentration
cim = CellVariable(name="$c_{im}$", mesh=m, value=0.0)

cm.constrain(0, m.facesLeft)
cm.constrain(0, m.facesRight)

cim.constrain(0, m.facesLeft)
cim.constrain(0, m.facesRight)

# advective flow velocity 
u = FaceVariable(mesh=m, value=(0.0,), rank=1)

# 1D convection diffusion equation (mobile domain)
# version with \frac{\partial c_{im}}{\partial t}
eqM =  (TransientTerm(1.0,var=cm) + TransientTerm(betaT,var=cim) == 
       DiffusionTerm(DR,var=cm) - ExponentialConvectionTerm(u/(Rm*phim),var=cm))

# immobile domain (lumped approach)
eqIM = TransientTerm(Rim*phiim,var=cim) == beta/Rim*(cm - ImplicitSourceTerm(1.0,var=cim))

# couple equations
eqn = eqM & eqIM

viewer = Viewer(vars=(cm,cim), datamin=0.0, datamax=1.0)
viewer.plot()
time = 0.0

for step in range(steps):
    time += timeStep

    if time < 0.5:
        u.setValue((1.0,))
    elif time < 1.0:
        u.setValue((0.0,))
    else:
        u.setValue((-1.0,))

    eqn.solve(dt=timeStep)
    viewer.plot()


