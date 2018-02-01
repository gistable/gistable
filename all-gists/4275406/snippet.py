# Problem 4-2
class edXPerson(Person):
    nextIdNum = 0
    def __init__(self, name):
        Person.__init__(self, name)
        self.idNum = edXPerson.nextIdNum
        edXPerson.nextIdNum += 1
    def getIdNum(self):
        return self.idNum
    def __lt__(self, other):
        if isinstance(self, SelfLearner):
            return self.name < other.name
        return self.idNum < other.idNum
    def isStudent(self):
        return isinstance(self, Student)
        
        
# Problem 4-3
class Subject(object):
    def __init__(self):
        self.students = []
    def addStudent(self, student):
        if student in self.students:
            raise ValueError('Duplicate student')
        self.students.append(student)
    def allStudents(self):
        for student in sorted(self.students):
            yield student
    def __str__(self):
        return 'Subject with ' + str(len(self.students)) + ' students.'


# Problem 7-1
def sampleQuizzes():
    return sum(70 <= ((0.25 * random.randint(50, 80)) + 
                      (0.25 * random.randint(60, 90)) + 
                      (0.5 * random.randint(55, 95))) <= 75 
               for __ in range(10000)) / float(10000)
               

# Problem 7-2
def plotQuizzes():
    results = generateScores(10000)
    pylab.hist(results, bins=7)
    pylab.title("Distribution of Scores")
    pylab.xlabel("Final Score")
    pylab.ylabel("Number of Trials")
    pylab.show()
    
    
# Problem 8-2
def probTest(limit):
    n = 1
    while ((5 ** (n - 1)) / float(6 ** n)) > limit:
        n += 1
    return n