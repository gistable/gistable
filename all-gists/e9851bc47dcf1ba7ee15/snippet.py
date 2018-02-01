import tank
from maya import cmds
path = cmds.file(q=True, sn=True)
tk = tank.tank_from_path(path)
ctx = tk.context_from_path(path)
tank.platform.start_engine('tk-maya', tk, ctx)