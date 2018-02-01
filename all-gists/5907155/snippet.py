class lukegoLRU:
    def __init__(self):
        # Initialize 'old' and 'new' to empty tables
        self.old = {}
        self.new = {}


    def insert(k, v):
        self.new[k] = v


    def lookup(k):
        if self.new.get(k):
            # Found in new table
            return self.new[k]
        elif self.old.get(k):
            # Migrate from old table to new table
            self.new[k] = self.old[k]
            return self.old[k]
        else:
            # Not found
            return None


    def age():
        # Entries in 'old' are dropped, entries in 'new' become old.
        self.old = self.new.copy()
        self.new = {} # empty table