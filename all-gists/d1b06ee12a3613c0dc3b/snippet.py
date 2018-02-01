class Fluent:
    def __init__(self, cache=None):
        self._cache = cache or []

    # Build the cache, and handle special cases
    def _(self, name):
        # Enables method chaining
        return Fluent(self._cache+[name])

    # Final method call
    def method(self):
        return self._cache

    # Reflection
    def __getattr__(self, name):
        return self._(name)

    # Called with the object is deleted
    def __del__(self):
        print('Deleting Myself')

fluent = Fluent()
chain = fluent.hello.world
print(chain.method())
# 'for' is a Python reserved word
new_chain = chain.thanks._('for').all.the.fish
print(new_chain.method())