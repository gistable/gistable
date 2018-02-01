import nuke
import random
import nukescripts

def runner():
    if nuke.thisKnob().name() == 'selected':
            # RANDOM FOR X
            random.seed(random.random())
            randFactX = (random.random()-0.5)
            # RANDOM FOR Y
            random.seed(random.random())
            randFactY = (random.random()-0.5)
            # RUN AWAY
            nuke.thisNode().setXpos(nuke.thisNode().xpos()+int(500*randFactX))
            nuke.thisNode().setYpos(nuke.thisNode().xpos()+int(500*randFactY))
            # CLEAR SELECTION
            nukescripts.clear_selection_recursive()

#nuke.removeKnobChanged( runner )
nuke.addKnobChanged( runner )