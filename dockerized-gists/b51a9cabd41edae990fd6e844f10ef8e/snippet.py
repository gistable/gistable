from thespian.actors import *
from datetime import datetime, timedelta
from logging import getLogger, basicConfig, DEBUG
from random import randint

basicConfig(level=DEBUG)
log = getLogger(__name__)


class Postman(Actor):
    def receiveMessage(self, msg, sender):
        print msg
        if msg == 'start':
            self.handleDeadLetters()
        elif msg == 'stop':
            self.handleDeadLetters(False)
        elif msg == 'count':
            self.send(sender, getattr(self, 'numDeadLetters', 0))
        elif isinstance(msg, ActorExitRequest):
            print "exiting"
            pass
        else:
            print "dead letter"
            self.numDeadLetters = getattr(self, 'numDeadLetters', 0) + 1

class RaftMessage(dict):
    def __init__(self, **kwargs):
        dict.__init__(self, kwargs)
        for k, v in kwargs.iteritems():
            self.__dict__[k] = v

FOLLOWER = 0
CANDIDATE = 1
LEADER = 2
LEADER_HEARTBEAT = timedelta(milliseconds=200)
VOTING_PERIOD = timedelta(milliseconds=500)

class ReliableActor(ActorTypeDispatcher):
    def __init__(self):
        ActorTypeDispatcher.__init__(self)
        self.peers = []
        self.state = FOLLOWER
        self.term = 0
        self.leader = None
        self.election_timeout = self.heartbeat_timeout = datetime.now() + LEADER_HEARTBEAT + self.interval()

    def interval(self):
        return timedelta(milliseconds=randint(150,300))

    def log(self, *args):
        print ['FOLLOWER','CANDIDATE','LEADER'][self.state], self.myAddress, " ".join(map(str,list(args)))

    def receiveMsg_str(self, msg, sender):
        #self.log("<-", sender, msg)
        if msg == "peers":
            self.send(sender, self.peers)
            self.wakeupAfter(self.interval())

    def start_election(self):
        self.state = CANDIDATE
        self.log("starting election")
        self.election_timeout = datetime.now() + VOTING_PERIOD
        self.leader = self.myAddress
        self.votes = 1
        self.term = self.term + 1
        for a in self.peers:
            self.send(a, RaftMessage(request_vote=True, term=self.term))
        self.wakeupAfter(VOTING_PERIOD/4)

    def receiveMsg_WakeupMessage(self, msg, sender):
        if self.state == LEADER:
            for a in self.peers:
                self.send(a, RaftMessage(heartbeat=True, term=self.term))
            self.wakeupAfter(LEADER_HEARTBEAT)
        elif self.state == FOLLOWER:
            if self.heartbeat_timeout < datetime.now():
                self.start_election()
            else:
                self.wakeupAfter(LEADER_HEARTBEAT)
        elif self.state == CANDIDATE:
            if self.election_timeout < datetime.now():
                self.start_election()
                return
            self.wakeupAfter(VOTING_PERIOD//2)

    def receiveMsg_RaftMessage(self, msg, sender):
        now = datetime.now()

        if 'new_peer' in msg:
            #self.log("<~", sender, msg)
            if msg['new_peer'] not in self.peers:
                self.peers.append(msg['new_peer'])

        if 'heartbeat' in msg and sender == self.leader:
            self.heartbeat_timeout = now + LEADER_HEARTBEAT + self.interval()

        if 'term' in msg and msg['term'] > self.term:
            self.state = FOLLOWER
            self.term = msg['term']
            self.leader = None

        if 'vote_granted' in msg and msg['vote_granted'] == True:
            self.log("<~", sender, msg)
            self.votes = self.votes + 1
            if self.votes > len(self.peers)//2:
                self.state = LEADER
                self.leader = self.myAddress
                self.log("am leader")
                self.votes = 0
                for a in self.peers:
                    self.send(a, RaftMessage(heartbeat=True, term=self.term))
                self.wakeupAfter(LEADER_HEARTBEAT)

        if 'request_vote' in msg:
            #self.log("<~", sender, msg)
            if self.state != LEADER:
                if not self.leader:
                    self.send(sender, RaftMessage(vote_granted=True, term=self.term))
                    self.leader = sender
                    #self.log("accepting", self.leader, "as leader")
                if self.leader != sender:
                    self.send(sender, RaftMessage(vote_granted=False, term=self.term))
                    #self.log("refusing", self.leader, "as leader")

if __name__ == "__main__":
    import sys
    #asys = ActorSystem((sys.argv + ['simpleSystemBase'])[1])
    asys = ActorSystem((sys.argv + ['multiprocUDPBase'])[1])

    actors = []

    o = asys.createActor('app.Postman', globalName="postman")
    asys.tell(o,'start')

    for n in range(5):
        actors.append(asys.createActor('app.ReliableActor'))
    for a in actors:
        for p in actors:
            if a != p:
                asys.tell(a, RaftMessage(new_peer=p))
    for a in actors:
        print len(asys.ask(a, "peers"))
    print asys.ask(o,"count")

    while True:
        asys.listen(timedelta(seconds=0.1))
    sys.exit(0)