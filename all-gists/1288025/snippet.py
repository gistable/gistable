from django.views.generic import dates
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Aggregate
from fallen.models import Casualty, Theater, Branch, HomeState, CauseOfDeath, IncidentProvince
from django.template.defaultfilters import upper
from haystack.views import SearchView
import datetime

class BaseFields(object):
    '''
    All of these views share an extra context dict containing counts for the various charts. Let's be a bit DRY about this.
    -----------------
    Hi, and welcome to annotation. I'm Jeremy, and I'll be your instructor today.
    We'll be adding these annotations to a dict which will be merged into the extra_context variable in every view.
    This example is about theaters, but it's the same logic for each of these.
    
    1.) Identify the model you want annotated counts of. In this case, it's Casualty.
    2.) Prepare a basic .filter() method to grab only the objects you want to count.
    3.) Prepare a .values() method to return just numbers, rather than full objects.
    4.) Add the .annotate() method. Annotate based on the field you're interested in counts for.
        WARNING #1: This will return just this field (e.g., name) rather than the Casualty OBJECT to the page. 
        WARNING #2: On the page, you can't just ask for foo in theater_chart, foo.id or foo.some_other field. Keep that in mind.
    5.) Order by field__count if you want the charts ordered by the count. Otherwise, just order by field or -field.
    
    Check the docs and the templates if you have questions.
    '''
    base_query = Casualty.safe_objects.all()
    
    def build_chart(base_query, field_name, order_by):
        '''
        This is a function to make building our charts a little DRYer. Beats the pants off of lambdas.
        '''
        return base_query.values(field_name).annotate(Count(field_name)).order_by(order_by)
    
    extra_context_dict = {}
    # All of these are easy, so let's just build the charts with a simple function.
    extra_context_dict['theater_chart']         = build_chart(base_query, 'theater__name', '-theater__name__count')
    extra_context_dict['branch_chart']          = build_chart(base_query, 'military_service_branch__name', '-military_service_branch__name__count')
    # extra_context_dict['year_chart']          = build_chart(base_query, 'death_date_year', '-death_date_year')
    extra_context_dict['sex_chart']             = build_chart(base_query, 'sex', '-sex__count')
    extra_context_dict['age_chart']             = build_chart(base_query, 'age_range', '-age_range__count')
    extra_context_dict['cause_chart']           = build_chart(base_query, 'cause_of_death__name', '-cause_of_death__name__count')
    extra_context_dict['total_count']           = base_query.count()
    extra_context_dict['now']                   = datetime.datetime.now()
    # These ones are harder/more complex. Rather than have a complex function for these, let's just build by hand.
    extra_context_dict['timeline']              = base_query\
                                                    .values('death_date_year')\
                                                    .annotate(Count('death_date_year'))\
                                                    .order_by('-death_date_year')

class BaseListFields(BaseFields):
    '''
    All of the list (e.g., non-detail) views share these three fields. Again, DRY isn't just for deserts.
    This is the basics necessary for the new class-based generic views.
    '''
    # I don't have to use this. But I am. So leave me alone.
    template_name                   = "casualty/casualty_list.html"
    
    # I want pagination. Check out the template for the names of all of the objects returned.
    paginate_by                     = 96
    
    # Returns our key queryset as this name. Plural for multiples, singular for just one.
    context_object_name             = "casualties"

class HomePage(BaseListFields, ListView):
    '''
    A list view of casualties modified to form a home page.
    '''
    # The other views below need to build more complex querysets using get_queryset().
    # This view is simple, and so it just clobbers the queryset variable.
    queryset                        = Casualty.safe_objects.all().order_by('-death_date').select_related()
    
    def get_context_data(self, *args, **kwargs):
        '''
        Defines a function which attaches context data to all pages.
        I'm not talking about this in such detail below, so this example will serve as your documentation for similar ones below.
        You're welcome.
        '''
        # Gotta get super(). Attach the get_context_data() method, since that's what we're super()ing.
        # The result of this will be a dict named context.
        context = super(HomePage, self).get_context_data(*args, **kwargs)
        
        # Here's what it looks like to add that extra context, via the dict .update() method.
        # This is grabbing that dict from the BaseListFields class and merging it into context.
        context.update(self.extra_context_dict)
        
        # Here's what it looks like to add some extra arbitrary content to context.
        context['page_class']           = '_home_page'
        
        # Return it.
        return context
    

class TheaterList(BaseListFields, ListView):
    def get_context_data(self, *args, **kwargs):
        context = super(TheaterList, self).get_context_data(*args, **kwargs)
        context.update(self.extra_context_dict)
        context['theater']              = get_object_or_404(Theater, slug=self.kwargs['theater_slug'])
        context['page_class']           = '_theater_list'
        return context
    
    def get_queryset(self):
        '''
        Defines a function which returns a queryset to build the list view from.
        Since this is the first time you may have seen get_queryset() clobbered, here's some instructions.
        I'm not repeating this below.
        Stop reading.
        Seriously.
        Still?
        C'mon.
        Argh.
        '''
        # When you see stuff like "self.kwargs['foo']", it's grabbing foo from the URL patterns in urls.py.
        # It's not magic. It's just neat that URL paths are returned as kwargs.
        return Casualty.safe_objects.filter(
                            theater__slug=self.kwargs['theater_slug']\
                        ).order_by('-death_date').select_related()