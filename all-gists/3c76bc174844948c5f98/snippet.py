from django.contrib.staticfiles.storage import staticfiles_storage
from pipeline.packager import Packager
from pipeline.conf import settings

def get_pipeline_urls(package_type, package_name):
    packager = Packager()
    package = packager.package_for(package_type, package_name)

    if settings.PIPELINE_ENABLED:
        return ( staticfiles_storage.url(package.output_filename), )
    else:
        files = ()
        for path in package.paths:
            files += ( staticfiles_storage.url(path), )
        return files

# Usage:
# ...
# class Media:
#     css = {
#         'all': get_pipeline_urls('css','your_css_package_name')
#     }
#     js = get_pipeline_urls('js','your_js_package_name')
# ...
