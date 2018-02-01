#----------------------------------------------------------------------------------------
# model.py
#----------------------------------------------------------------------------------------
from django.db import models
from numpy.random import random_sample

class CustomModel(models.Model):
    # Put your fields here

    def get_data(self):
        """ 
        Fake Method to generate random data.
        In the real case, this method should arrange
        data to be plotted according to model instance
        fields' values.
        """
        return random_sample(5)

#----------------------------------------------------------------------------------------
# admin.py
#----------------------------------------------------------------------------------------
from django.contrib import admin
from django.shortcuts import render
from django.http import Http404
from .models import CustomModel

class CustomModelAdmin(admin.ModelAdmin):

    def get_urls(self):
        """
        Add additional view to ModelAdmin urls
        """
        urls = super(CustomModelAdmin, self).get_urls()
        my_urls = patterns('',
                           url(r'^(?P<instance_id>\d+)/view_mpld3_chart/$',
                               self.view_chart, name='view_chart'),
                           )
        return my_urls + urls

    # ==============================
    # Model Admin custom view method
    # ==============================

    def view_chart(self, request, instance_id):
        from matplotlib.pyplot import figure, title, bar
        import numpy as np
        import mpld3

        mpl_figure = figure(1, figsize=(6, 6))
        xvalues = range(5)  # the x locations for the groups

        try:
            model_object = CustomModel.objects.get(pk=instance_id)
            yvalues = model_object.get_data()
        except CustomModel.DoesNotExist:
            yvalues = np.random.random_sample(5)

        width = 0.5  # the width of the bars    
        title(_(u'Custom Bar Chart'))
        bar(xvalues, yvalues, width)
        fig_html = mpld3.fig_to_html(mpl_figure)

        return render('admin/custom_template.html',
                                  {'figure': fig_html, 'opts': self.model._meta, 
                                  'app_label': self.model._meta.app_label,},
                                  context_instance = RequestContext(request))
                                  
admin.site.register(CustomModel, CustomModelAdmin)  # Register the Model in the AdminSite
#----------------------------------------------------------------------------------------
# DJANGO TEMPLATE: admin/custom_template.html
#----------------------------------------------------------------------------------------

{% extends "admin/change_form.html" %}
{% load i18n %}

{% block extrahead %}
    {{ block.super }}
    <style type="text/css">
        .chart_title {
            font-weight: bold;
            font-size: 14px;
        }
    </style>
{% endblock %}

{% block content %}
    <div id="content-main">

        <div class="chart_title">
            {% trans "Custom Bar Chart" %}
        </div>
        {{ figure|safe }}
    </div>
{% endblock %}