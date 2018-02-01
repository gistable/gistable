x = input("What programming language do you know ?") 

keywords = ["Python", "JavaScript", "Ruby"] 

if any(keyword in x for keyword in keywords): 
print("I know that language also !")