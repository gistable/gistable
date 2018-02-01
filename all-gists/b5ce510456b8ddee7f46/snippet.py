_author_ = 'Ernie'
from operator import attrgetter, itemgetter
#---------------Set-up-room-object------------------
class Room:
	def _init_(self,roomNumber,roomSize):
		self.roomNumber = roomNumber
		self.roomSize = roomSize
		roomNumber = 0
		roomSize = 0
#---------------Set-up-class-object-----------------
class CollClass:
	def _init_(self,className,classSize,classPer):
		self.className = className
		self.classSize = classSize
		self.classPer = classPer
		className = ""
		classSize = 0
		classPer = 0
#--------------Set-up-empty-lists--------------------
classes = []
rooms = []
roomSizes= []
loserClasses = []
periods = []
#--------------Popluate-class-list-------------------
with open("classList.txt","r") as filestream:
	for line in filestream:
		currentline = line.split(",")
		classobj= CollClass()
		classobj.className = currentline[0]
		classobj.classSize = int(currentline[1])
		classobj.classPer = int(currentline[2])
		classes.append(classobj)
		periods.append(int(currentline[2]))
#--------------Populate-room-list---------------------
with open("Rooms.txt","r") as filestream:
	for line in filestream:
		currentline = line.split(",")
		roomobj = Room()
		roomobj.roomNumber = currentline[0]
		roomobj.roomSize = currentline[1]
		roomSizes.append(roomobj.roomSize)
		rooms.append(roomobj)
#--------------Sort-the-lists-------------------------
rooms.sort(key=attrgetter('roomSize'))
roomSizes.sort()
classes.sort(key=attrgetter('classPer','classSize'))
#-------------Schedule-the-lists----------------------
with open("classResults","w") as filestream:
	for i in range(len(classes)):                                               #print out sorted classes
		filestream.write("Class: %s, Class Size: %s, Class Period: %s\n" % (classes[i].className,classes[i].classSize,classes[i].classPer))
		#print "Class: %s, Class Size: %s, Class Period: %s" % (classes[i].className,classes[i].classSize,classes[i].classPer)
	for i in range(len(rooms)):                                                                 #print out sorted rooms
		filestream.write("Room: %s, Capacity: %s" % (rooms[i].roomNumber,rooms[i].roomSize) )
		#print "Room: %s, Capacity: %s" % (rooms[i].roomNumber,rooms[i].roomSize)
	filestream.write("\n------Optimal Scheduling:-------")
	#print "------Class Scheduling:-------"                                       #now the schedule
	for p in range(max(periods)):
		filestream.write("\nFor Period %d:\n"%int(p+1))                      #for each period
		#print "For Period %d:\n"%int(p+1)                        #for each period
		for j in range(len(classes)):
			if int(classes[j].classPer) == p+1:
				min_difference = float("inf")                                                   #begin with min_diff set to infinity
				for k in range(len(rooms)):
					if int(classes[j].classSize) <=int(rooms[k].roomSize) < min_difference:   #if the room is bigger than the class and smaller than the smallest amount of remaining seats
						min_difference = int(classes[j].classSize) - int(rooms[k].roomSize)
						best_fit = rooms[k]                                                                 #that room will become the best fit for the class
						rooms[k].roomSize = 0                                                               #room becomes unavailable
						classes[j].classSize = 0                                                        #class becomes available
						filestream.write("\nClass: %s, to be held in Room %s" % (classes[j].className,best_fit.roomNumber))     #Print out the scheduled class
						#print "Class: %s, fits best in %s" % (classes[j].className,best_fit.roomNumber)
				if classes[j].classSize != 0:                                                       #if any class not made unavailable, is unmatched
					loserClasses.append(classes[j].className)                           #send that class to the loser bin
		for k in range(len(rooms)):
			rooms[k].roomSize = int(roomSizes[k])                               #rooms become available again ,start over for next period
	#print ""
	for i in range(len(loserClasses)):                                                      #after schedule, print out the loser bin
		#print "TBA: %s"%loserClasses[i]
		filestream.write("\nTBA: %s"%loserClasses[i])