# [your-project/context_processors.py]
from django.conf import settings

def ssl_fix(request):
    media_url = getattr(settings, 'MEDIA_URL')
    if request.is_secure() == True:
        media_url = media_url.replace("http://", "https://")
    
    return {
        "MEDIA_URL": media_url,
    }

# [your-project/settings.py]
TEMPLATE_CONTEXT_PROCESSORS = (
    "other_processor_defined_already",
    "your-project.context_processors.ssl_fix",
)
