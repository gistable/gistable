#inherit.py

class SchoolMember:

      '''Represents any school member'''
      def __init__(self, name, age):
          self.name = name
          self.age = age
          print 'Initialized SchoolMember constructor: %s' % self.name

      def tell(self):
          '''Tell me datails'''
          print 'Name: "%s", Age: "%s"' % (self.name, self.age)


class Teacher(SchoolMember):

       '''Represents any teacher'''
       def __init__(self,name,age,salary):
           SchoolMember.__init__(self,name,age)
           self.salary = salary
           print '(Initialized Teacher: %s)' % self.name 

       def tell(self):
           SchoolMember.tell(self) 
           print 'salary: %s' % self.salary


class Student(SchoolMember):
       '''Represents any student'''
       def __init__(self,name,age,marks):
           SchoolMember.__init__(self,name,age)
           self.marks = marks
           print '(Initialized Student: %s)' % self.name 

       def tell(self):
           SchoolMember.tell(self)
           print 'marks: %s' % self.marks

prof = Teacher('Victor Mitrana',50,7000)
gibon = Student('Rasmus',30,97)

members = [prof,gibon]
for member in members:
    member.tell() 