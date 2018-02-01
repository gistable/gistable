from wsgiref.simple_server import make_server
from webob.dec import wsgify

class OTree(object):
    def __init__(self, name=""):
        self.children = {}
        self.name = name
        self.fn = None

    def _get_name(self, child, name):
        name = name or (child.name if hasattr(child, "name") else None)
        if name is None:
            raise Exception("name is not found")
        return name

    def add_child(self, child, name=None):
        name = self._get_name(child, name)
        self.children[name] = child
        return child

    def finished(self, node_list):
        return node_list == []

    def _delegate(self, node_list):
        if self.finished(node_list):
            return self
        current = node_list.pop(0)
        return self.children[current]._delegate(node_list)

    def delegate(self, path):
        node_list = path.split("/")
        return self._delegate([x for x in node_list if x != ""])
    
    def __getattr__(self,k):
        return self.children.get(k) or self.__class__(name=k)

    ## as decorator
    def bind(self, fn):
        def _bind(request):
            return self.delegate(request.path).fn(request)
        self.fn = fn
        return _bind



# root = OTree("")
# root.add_child(root.x)
# root.x.add_child(root.x.y)
# assert root.delegate("/") == root
# assert root.delegate("") == root
# assert root.x == root.delegate("x")
# assert root.x.y == root.delegate("x/y")

root = OTree()
@wsgify
@root.bind
def toplevel(request):
    return "hee. this is top level"

child0 = root.add_child(root.child0)
@wsgify
@child0.bind
def child0(request):
    return "this is child node"

child1 = root.add_child(root.child1)
@wsgify
@child1.bind
def child1(request):
    return "this is child node"

grand_child = root.child1.add_child(root.child1.grand_child)

@wsgify
@grand_child.bind
def grand_child(request):
    return "top / child1 / grand chlid"


if __name__ == '__main__':
    httpd = make_server('', 8080, toplevel)
    import sys
    sys.stderr.write("port:{0}".format(8080))
    httpd.serve_forever()
