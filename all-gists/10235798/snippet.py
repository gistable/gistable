from django.http import HttpResponse

PIXEL_GIF_DATA = """
R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7
""".strip().decode('base64')

def pixel_gif(request):
    return HttpResponse(PIXEL_GIF_DATA, content_type='image/gif')
