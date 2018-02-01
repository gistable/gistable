class JSONMiddleware(object):
    """
    Process application/json requests data from GET and POST requests.
    """
    def process_request(self, request):
        if 'application/json' in request.META['CONTENT_TYPE']:
            # load the json data
            data = json.loads(request.body)
            # for consistency sake, we want to return
            # a Django QueryDict and not a plain Dict.
            # The primary difference is that the QueryDict stores
            # every value in a list and is, by default, immutable.
            # The primary issue is making sure that list values are
            # properly inserted into the QueryDict.  If we simply
            # do a q_data.update(data), any list values will be wrapped
            # in another list. By iterating through the list and updating
            # for each value, we get the expected result of a single list.
            q_data = QueryDict('', mutable=True)
            for key, value in data.iteritems():
                if isinstance(value, list):
                    # need to iterate through the list and upate
                    # so that the list does not get wrapped in an
                    # additional list.
                    for x in value:
                        q_data.update({key: x})
                else:
                    q_data.update({key: value})

            if request.method == 'GET':
                request.GET = q_data

            if request.method == 'POST':
                request.POST = q_data

        return None