def conversation(conversation_dict):
    conversations=[i for i in conversation_dict]
    for index,conv in enumerate(conversations):
        print("{0}. {1}".format(index+1,conv))
    choice=int(input("What do you say (enter number)?"))
    outcome=conversation_dict[conversations[choice-1]]
    if not type(outcome)==dict:
        outcome()
    else:
        conversation(outcome)

def AI_reply_function():
    print("I am just a guard")

def AI_fight():
    print("You flail your arms about but your enemy kills you")

def AI_job():
    print("I used to be an adventurer like you, but then I took an arrow in the knee.")

def show_map():
    print("X marks the spot")

sample_convo={
              "Who are you?":AI_reply_function,
              "I challenge you to a duel":AI_fight,
              "I'd like to know something":{
                                            "What do you do for a living":AI_job,
                                            "How do I reach Riverrun?":show_map
                                           }
             }


conversation(sample_convo)