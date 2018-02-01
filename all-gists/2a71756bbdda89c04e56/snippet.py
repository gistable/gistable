API_RECURSION_LIMIT = 5

def get_stories(object_id):
    token = facebook.get_app_access_token(APP_ID, APP_SECRET)
    graph = facebook.GraphAPI(token)

    def get_interesting_stories(until=None, since=None, recursion_level=0):
        """Recursive function that digs all the interesting stories till the recursion level is reached"""
        api_parameters = {
            'id': '{page_id}/feed'.format(page_id=object_id),
            'fields': ['message', 'story', 'link', 'description', 'caption', 'status_type'],
            'limit': 50,
        }
        if until:
            api_parameters['until'] = until
        if since:
            api_parameters['since'] = since

        response = graph.get_object(**api_parameters)
        feed = response['data']

        if 'paging' in response and 'next' in response['paging'] and recursion_level < API_RECURSION_LIMIT:
            query = parse_qs(urlparse(response['paging']['next']).query)
            new_until = query.get('until', None)
            new_since = query.get('since', None)
            next_kwargs = {
                'recursion_level': recursion_level+1,
            }

            if new_until:
                next_kwargs['until'] = new_until[0]
            if new_since:
                next_kwargs['since'] = new_since[0]

            feed += get_interesting_stories(**next_kwargs)

        return [story for story in feed if story.get('status_type', None) == 'shared_story']
