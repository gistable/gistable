def liar(answer):
 return !answer
 
def honest(answer):
 return answer
 
#"Would that door say that this is the door to the castle?"
#if asking the liar, and the liar is the death door:
print(liar(honest(false)))   # "True"

#if asking the liar, and the liar is the castle door:
print(liar(honest(true)))    # "False"

#if asking the honest door, and the honest door is the death door:
print(honest(liar(false)))   # "True"

#if asking the honest door, and the honest door is the castle door:
print(honest(liar(true)))    # "False"