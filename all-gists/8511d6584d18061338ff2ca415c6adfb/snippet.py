class vehicle:
 def __init__(self,noofwheels):
  self.noofwheels=noofwheels
 def disp(self):
  print 'The no of wheels is %d'%(self.noofwheels)
class car(vehicle):
 def __init__(self,fuel):
  self.fuel=fuel
  x=input('Please enter the no of wheels : ')
  vehicle.__init__(self,x)
class model(car):
 def __init__(self,name):
  self.name=name
  y=raw_input('Please enter the fuel type : ')
  car.__init__(self,y)
 def disp(self):
  print 'The car model is %s\nFuel type is %s\nNo of wheels is %d'%(self.name,self.fuel,self.noofwheels)

m1=model('BMW')
m1.disp() 
