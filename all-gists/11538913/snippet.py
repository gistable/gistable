import chimera
from DockPrep import prep
models = chimera.openModels.list(modelTypes=[chimera.Molecule])
prep(models)
from WriteMol2 import writeMol2
writeMol2(models, "dp.mol2")