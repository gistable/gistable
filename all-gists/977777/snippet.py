from twisted.internet import reactor, defer


class Api:
  def __init__(self):
    self.domainObjects = None
    self.subscribers = []

  def test(self, url):
     # code for doing the async stuff here
      d = defer.Deferred()
      d.addCallback(self.asyncFinishedHandler)
      reactor.callLater(3, d.callback, 100)

  def asyncFinishedHandler(self, response):
     # parse response into domain objects
      parseResults = self.parse(response)
      self.domainObjects = parseResults
      self.__raiseDoneEvent()

  def __raiseDoneEvent(self):
    for s in self.subscribers:
      s()

  def parse(self, response):
    return response

  def subscribeToDoneEvent(self, subscriber):
    self.subscribers.append(subscriber)
 
def main(): 
  a = Api()

  def doneEventHandler():
    print a.domainObjects
  a.subscribeToDoneEvent(doneEventHandler)
  a.test("something")
  reactor.callLater(4, reactor.stop)
  reactor.run()

if __name__ == "__main__":
  main()
