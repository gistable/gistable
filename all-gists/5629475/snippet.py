class CustomSpider(BaseSpider):
    def __init__(self, start_url=None, **kwargs):
        super(BaseSpider, self).__init__(*args, **kwargs)
        if start_url:
            self.start_url = start_url

    def start_requests(self):
        return [Request(self.start_url)]