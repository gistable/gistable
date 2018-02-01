from django.conf import settings


def global_settings(request):
    # return any necessary values
    return {
        'GOOGLE_ANALYTICS': settings.GOOGLE_ANALYTICS,
        'GOOGLE_API_KEY': settings.GOOGLE_API_KEY
    }