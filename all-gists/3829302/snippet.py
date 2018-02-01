from django.template.defaultfilters import slugify
from django.contrib.sites.models import Site
from django.core.files import File
from taggit.models import Tag
from .models import Photo
import factory
import os

TEST_MEDIA_PATH = os.path.join(os.path.dirname(__file__), 'tests', 'test_media')
TEST_PHOTO_PATH = os.path.join(TEST_MEDIA_PATH, 'test_photo.png')


class PhotoFactory(factory.Factory):
    FACTORY_FOR = Photo

    title = factory.Sequence(lambda n: 'Test Photo {0}'.format(n))
    slug = factory.LazyAttribute(lambda a: slugify(a.title))
    status = 'P'
    photo = factory.LazyAttribute(lambda a: File(open(TEST_PHOTO_PATH)))

    @factory.post_generation(extract_prefix='tags')
    def add_default_tags(self, create, extracted, **kwargs):
        # allow something like ArticleFactory(tags=Tag.objects.all())
        if extracted and type(extracted) == type(Tag.objects.all()):
            self.tags = extracted
            self.save()
        else:
            self.tags.add("lorem", "ipsum", "dolor")

    @factory.post_generation(extract_prefix='sites')
    def add_default_site(self, create, extracted, **kwargs):

        # allow something like ArticleFactory(sites=Site.objects.all())
        if extracted and type(extracted) == type(Site.objects.all()):
            self.sites = extracted
            self.save()
        else:
            self.sites.add(Site.objects.get_current())
            self.save()
