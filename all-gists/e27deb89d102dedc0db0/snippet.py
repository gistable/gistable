# views.py - django app called ajx
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse, render_to_response, HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.contrib.auth import authenticate, login
import json

def mygetview(request):
    if request.method == 'GET':

        print "**get**"
        data = request.GET['mydata']
        astr = "<html><b> you sent a get request </b> <br> returned data: %s</html>" % data
        return HttpResponse(astr)
    return render(request)

def mypostview(request):
    if request.method == 'POST':

        print "**post**"
        data = request.POST['mydata']
        astr = "<html><b> you sent a post request </b> <br> returned data: %s</html>" % data
        return HttpResponse(astr)
    return render(request)

def myajaxview(request):
    if request.method == 'POST':
        if request.is_ajax():
            print "**ajax post**"
            data = request.POST['mydata']
            astr = "<html><b> you sent an ajax post request </b> <br> returned data: %s</html>" % data
            return HttpResponse(astr)
    return render(request)

def myajaxformview(request):
    if request.method == 'POST':
        if request.is_ajax():
            import json

            print "**ajax form post**"
            for k,v in request.POST.items(): 
                print k,v

            print "field1 data: %s" % request.POST['field1']
            print "field2 data: %s" % request.POST['field2']

            mydata = [{'foo':1, 'baz':2}]
            return HttpResponse(json.dumps(mydata), mimetype="application/json")
    
    return render(request)

def foo(request,template='ajx/foo.html'):
    return render(request,template)

# urls.py

from django.conf.urls import patterns, url
#from .views import ThingList, ThingCreate, ThingDetail, ThingUpdate, ThingDelete
from . import views

urlpatterns = patterns(
    '',
    url(r'^foo', views.foo, name='foo'),
    url(r'^mygetview', views.mygetview, name='mygetview'),
    url(r'^mypostview', views.mypostview, name='mypostview'),
    url(r'^myajaxview', views.myajaxview, name='myajaxview'),
    url(r'^myajaxformview', views.myajaxformview, name='myajaxformview'),
    #url(r'^formview1', views.formview1, name='formview1'),
    #url(r'^register', views.register, name='register'),
    #url(r'^login', views.user_login, name='login'),
    #url(r'^$', ThingList.as_view(), name='thing_list'),
    #url(r'^new/$', ThingCreate.as_view(), name='thing_create'),
    #url(r'^(?P<pk>\d+)/$', ThingDetail.as_view(), name='thing_detail'),
    #url(r'^(?P<pk>\d+)/update/$', ThingUpdate.as_view(), name='thing_update'),
    #url(r'^(?P<pk>\d+)/delete/$', ThingDelete.as_view(), name='thing_delete'),
)

# foo.html - located in: templates/ajx/
<!DOCTYPE html>
<html>
<head>
<script src="http://code.jquery.com/jquery-1.10.1.min.js"></script>
<script type="text/javascript">
$(function() {
  var count = 0;
  $('#mybutton').click(function() {
      $.get('/ajx/mygetview', {'mydata': 'xyz'}, function(data) {
        $('#output').html(data); // append to inner html
        //alert(data);
    });
  });
  $('#mybutton2').click(function() {
      // You gotta include the csrf_token in your post data
      $.post('/ajx/mypostview', {'mydata': 'xyz', 'csrfmiddlewaretoken': '{{ csrf_token }}'}, function(data) {
        $('#output').html(data); // append to inner html
        //alert(data);
    });
  });

  $('#mybutton3').click(function(event) {
      // You gotta include the csrf_token in your post data
    event.preventDefault();
    $.ajax({
        type: 'POST',
        url: '/ajx/myajaxview',
        data: {'mydata': 'xyz', 'csrfmiddlewaretoken': '{{ csrf_token }}'},
        success: function (data, textStatus) {
            //alert(data, textStatus);
            $('#output').html(data); // append to inner html
        },
        error: function(xhr, status, e) {
            alert(status, e);
        }
    });
  });

  $('#myform').submit(function(event) {
    // You gotta include the csrf_token in your post data
    event.preventDefault();
    $.ajax({
        type: 'POST',
        url: '/ajx/myajaxformview',
        dataType: 'json',
        data: $('#myform').serialize(), // serialize all your 
        success: function (data, textStatus) {
            //alert(JSON.stringify(data), textStatus);
            count += 1;
            $('#output2').html("");
            $('#output2').html(count + " - You sent a ajax form post. Here's the data from server" + JSON.stringify(data)); // append to inner html
        },
        error: function(xhr, status, e) {
            alert(status, e);
        }
    });
  });

});
</script>
</head>
<body>
  <button id="mybutton"> Click me - GET </button>
  <button id="mybutton2"> Click me - POST </button>
  <button id="mybutton3"> Click me - AJAX </button>
  <div id="output"></div>

<br />
<br />

  <form id="myform" method="post" action="/rango/login/">
    {% csrf_token %}
    Field1: <input type="text" name="field1" value="" size="50" />
    <br />
    Field2: <input type="text" name="field2" value="" size="50" />
    <br />

    <input type="submit" value="Click me- AJAX form" /></input>
  </form>
  <div id="output2"></div>

</body>
</html>