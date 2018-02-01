import time


class PageCategoryFilter(object):
    def __init__(self, config):
        self.mode = config["mode"]
        self.categories = config["categories"]

    def filter(self, bid_request):
        if self.mode == "whitelist":
            return bool(bid_request["categories"] & self.categories)
        else:
            return bool(
                self.categories and not
                bid_request["categories"] & self.categories
            )


def page_category_filter(bid_request, config):
    if config["mode"] == "whitelist":
        return bool(bid_request["categories"] & config["categories"])
    else:
        return bool(
            config["categories"] and not
            bid_request["categories"] & config["categories"]
        )


def make_page_category_filter(config):
    categories = config["categories"]
    mode = config["mode"]
    def page_category_filter(bid_request):
        if mode == "whitelist":
            return bool(bid_request["categories"] & categories)
        else:
            return bool(
                categories and not
                bid_request["categories"] & categories
            )

    return page_category_filter


def test(N):
    filters = [
        PageCategoryFilter(dict(mode="whitelist", categories=set(["foo", "bar", "baz"]))),
        PageCategoryFilter(dict(mode="blacklist", categories=set(["foo", "bar", "baz"]))),
        PageCategoryFilter(dict(mode="whitelist", categories=set([]))),
        PageCategoryFilter(dict(mode="blacklist", categories=set([]))),
    ]

    bid_request = {"categories": set("bat")}
    start = time.time()
    for _ in xrange(N/4):
        for a_filter in filters:
            a_filter.filter(bid_request)
    end = time.time()

    t_class = end - start


    configs = [
        dict(mode="whitelist", categories=set(["foo", "bar", "baz"])),
        dict(mode="blacklist", categories=set(["foo", "bar", "baz"])),
        dict(mode="whitelist", categories=set()),
        dict(mode="blacklist", categories=set()),
    ]

    bid_request = {"categories": set("bat")}
    start = time.time()
    for _ in xrange(N/4):
        for config in configs:
            page_category_filter(bid_request, config)
    end = time.time()

    t_func = end - start


    filters = [
        make_page_category_filter(dict(mode="whitelist", categories=set(["foo", "bar", "baz"]))),
        make_page_category_filter(dict(mode="blacklist", categories=set(["foo", "bar", "baz"]))),
        make_page_category_filter(dict(mode="whitelist", categories=set())),
        make_page_category_filter(dict(mode="blacklist", categories=set())),
    ]

    bid_request = {"categories": set("bat")}
    start = time.time()
    for _ in xrange(N/4):
        for a_filter in filters:
            a_filter(bid_request)
    end = time.time()

    t_closure = end - start

    return (t_class, t_func, t_closure)

if __name__ == "__main__":
    import sys

    if "warmup" in sys.argv:
        test(100000)

    N = 15000000
    t_class, t_func, t_closure = test(N)

    print "class  ", t_class, t_class / N
    print "func   ", t_func, t_func / N
    print "closure", t_closure, t_closure / N
