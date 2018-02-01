# from the whiskey engine example

# uses the Sharrock RPC client (https://github.com/Axilent/sharrock).  Created by us, but open source, not specific to the Axilent API.
from sharrock.client import HttpClient, ResourceClient

# some things in the API are modeled as RESTful resources and use the ResourceClient, others are straight RPC and use the HttpClient
axl = HttpClient('%s/api' % settings.AXILENT_ENDPOINT,'axilent.content','beta3',auth_user=settings.AXILENT_API_KEY)
content_resource = ResourceClient('%s/api/resource' % settings.AXILENT_ENDPOINT,'axilent.content','beta3','content',auth_user=settings.AXILENT_API_KEY)

# Featured Whiskey
featured_whiskey = None
if whiskey_slug:
    # In this case the name of the whiskey has been specified
    featured_whiskey = axl.getcontentbyuniquefield(content_type='Whiskey',field_name='slug',field_value=whiskey_slug)
else:
    # In this case we're pulling from a content channel - it's set to random, but can be changed in Axilent at any time
    # without any reprogramming here.
    featured_whiskey = axl.contentchannel(channel='random-whiskey')['default'][0]['content']


# Search
results = axl.search(content_types='Whiskey',query=request.GET['q']) # 'q' is the query