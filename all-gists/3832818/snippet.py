from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site
from django.db import transaction

from cms.models import Page


class Command(BaseCommand):
    help = 'Copy the CMS pagetree from a specific SITE_ID.'
    option_list = BaseCommand.option_list + (
        make_option('--from', dest='from_site', default=None,
            help='Specifies the SITE_ID to copy from.'),
        make_option('--to', dest='to_site', default=None,
            help='Specifies the SITE_ID to copy to.')
    )

    def handle(self, *args, **options):
        from_site = options.get('from_site', None)
        to_site = options.get('to_site', None)

        if not from_site or not to_site:
            raise CommandError("You must use --from and --to to use this command.")

        self.get_site(from_site)
        site = self.get_site(to_site)
        pages = Page.objects.filter(site=from_site, level=0)

        with transaction.commit_on_success():
            for page in pages:
                page.copy_page(None, site)

            Page.objects.filter(site=to_site).update(published=True)
            self.stdout.write("Copied CMS Tree from SITE_ID {0} successfully to SITE_ID {1}.\n".format(from_site, to_site))


    def get_site(self, site_id):
        try:
            return Site.objects.get(pk=site_id)
        except Site.DoesNotExist:
            raise CommandError("\nUnknown site: {0}. Please create a new site first.\n".format(site_id))
