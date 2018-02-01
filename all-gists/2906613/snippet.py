class Cutie:
  def __init__(self, name, cuteness):
    self.name = name
    self.cuteness = cuteness

  def describe(self):
    return self.name + " is " + "very " * self.cuteness + "cute"

print Cutie("Edmund", 10).describe()
