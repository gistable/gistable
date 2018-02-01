class MixPanel(object):

    def get_page_view_funnel(self, content_urls):
        # Build up the events array. Each "event" is a step in the funnel
        events = []
        for cu in content_urls:
            events.append({
                "event": "Page View",
                "selector": 'properties["Page View Page"] == "%s"' % (cu,),
            })

        return self.request(["arb_funnels"], {
            "events": events,

            # The time window to query over.
            "from_date": start_dt.strftime("%Y-%m-%d"),
            "to_date": end_dt.strftime("%Y-%m-%d"),

            # The next two parameters control how the server aggregates the 
            # data before returning it to you, so you should very carefully
            # select these to return only the information you need.

            # This groups the data points based on their properties. We have
            # 3 possible values for User Type: Logged In, Phantom (our name for
            # "Logged Out"), and New (registered in the past month).
            "on": 'properties["User Type"]',

            # The time level at which
            # This can be 'minute', 'hour', 'day', 'week', or 'month'.
            # It determines the level of granularity of the data you get back.
            "unit": 'month'
        })