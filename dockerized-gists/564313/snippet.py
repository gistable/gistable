"""
I've been thinking lately about how perfect Redis would be for storing a
simple social graph. I posited that it would be relatively few lines of code,
and that it'd be clean code too. So here it is: a basic social graph built on Redis.
"""

class FriendGraph(object):
    
    def __init__(self, ring):
        self.ring = ring
        
        # These keys are intentionally short, so as to save on memory in redis
        self.FOLLOWS_KEY = 'F'
        self.FOLLOWERS_KEY = 'f'
        self.BLOCKS_KEY = 'B'
        self.BLOCKED_KEY = 'b'
    
    def follow(self, from_user, to_user):
        forward_key = '%s:%s' % (self.FOLLOWS_KEY, from_user)
        forward = self.ring.sadd(forward_key, to_user)
        reverse_key = '%s:%s' % (self.FOLLOWERS_KEY, to_user)
        reverse = self.ring.sadd(reverse_key, from_user)
        return forward and reverse
    
    def unfollow(self, from_user, to_user):
        forward_key = '%s:%s' % (self.FOLLOWS_KEY, from_user)
        forward = self.ring.srem(forward_key, to_user)
        reverse_key = '%s:%s' % (self.FOLLOWERS_KEY, to_user)
        reverse = self.ring.srem(reverse_key, from_user)
        return forward and reverse
    
    def block(self, from_user, to_user):
        forward_key = '%s:%s' % (self.BLOCKS_KEY, from_user)
        forward = self.ring.sadd(forward_key, to_user)
        reverse_key = '%s:%s' % (self.BLOCKED_KEY, to_user)
        reverse = self.ring.sadd(reverse_key, from_user)
        return forward and reverse
    
    def unblock(self, from_user, to_user):
        forward_key = '%s:%s' % (self.BLOCKS_KEY, from_user)
        forward = self.ring.srem(forward_key, to_user)
        reverse_key = '%s:%s' % (self.BLOCKED_KEY, to_user)
        reverse = self.ring.srem(reverse_key, from_user)
        return forward and reverse
    
    def get_follows(self, user):
        follows = self.ring.smembers('%s:%s' % (self.FOLLOWS_KEY, user))
        blocked = self.ring.smembers('%s:%s' % (self.BLOCKED_KEY, user))
        return list(follows.difference(blocked))
    
    def get_followers(self, user):
        followers = self.ring.smembers('%s:%s' % (self.FOLLOWERS_KEY, user))
        blocks = self.ring.smembers('%s:%s' % (self.BLOCKS_KEY, user))
        return list(followers.difference(blocks))
    
    def get_blocks(self, user):
        return list(self.ring.smembers('%s:%s' % (self.BLOCKS_KEY, user)))
    
    def get_blocked(self, user):
        return list(self.ring.smembers('%s:%s' % (self.BLOCKED_KEY, user)))