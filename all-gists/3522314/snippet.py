class Accessor(object):
    def __init__(self, wrapper, d):
        self.wrapper = wrapper
        self.d = d

    def __repr__(self):
        return repr(self.d)

    def _get_failback(self, k):
        chained = self.wrapper.chained
        if chained:
            return chained.data[k]

    def __getitem__(self, k):
        if self.d is None:
            return None
        return self.d.get(k) or self._get_failback(k)

    def getall(self, k):
        r = []
        this = self.wrapper
        while this:
            v = this.data.d.get(k)
            if v:
                r.append(v)
            this = this.chained
        return r

    def access(self, target):
        return target

class Traverser(object):
    def __init__(self, accessor_impl=Accessor):
        self.chained = None
        self.target = None
        self._configured = False
        self._accessor_impl = accessor_impl

    def traverse(self, target):
        if not self._configured:
            getattr(self, "traverse_"+(target.__class__.__name__))(target)
            self._configured = True
        return self

    def _set_data(self, data):
        self._data = data
        self.data = self._accessor_impl(self, data)

    def traverse_MoreSpecific(self, s):
        specific = s.specific
        self.target = s
        self._set_data(s.extra_info)

        self.chained = self.__class__(accessor_impl=self._accessor_impl)
        self.chained.traverse(specific)

    def traverse_Specific(self, s):
        item = s.item
        self.target = s
        self._set_data(s.extra_info)

        self.chained = self.__class__(accessor_impl=self._accessor_impl)
        self.chained.traverse(item)

    def traverse_Item(self, item):
        self.target = item
        self._set_data(item.info)


class Item:
    info = {"data": "something", "name": "item"}
class Specific:
    extra_info = {"data": "anything"}
    item = Item()
class MoreSpecific:
    extra_info = {"description": "this-is-long-text"}
    specific = Specific()

trv = Traverser().traverse(MoreSpecific())
trv.data["data"] # => anything
trv.data["name"] # => item
trv.data["description"] # => this-is-long-text

print trv.data.getall("data") # => ['anything', 'something']
