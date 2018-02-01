Step 1: Create Movie Add form



	• movies.html
        <form action="/movies/" method="post"> {% csrf_token %}
            Movie Name: <input type="Text" name="name"> <input type="submit" value="Add">
        </form>

	• views.py
	    return render(request, "movies.html")

	• Enable it in the urls.py


Step 2: Implement Add Movie & Persist  in the database

	• models.py
		class Movie(models.Model):
		    name = models.CharField(max_length=100, unique=True)
		
		    def __unicode__(self):
		        return self.name
		
	• Run sync db
		
	• views.py
		def movies(request):
		    if request.method == 'GET':
		        return render(request, "movies.html")
		    if request.method == 'POST':
		        name = request.POST.get('name', None)
		        Movie.objects.create(name=name)
		        return HttpResponse("Movie '%s' added successfully!" % name)
		    return HttpResponse("Invalid Request")
		
Step 3: Implement  Messaging in the same page
	
	• movies.html
	
	{% if message %}
    		{{ message }} <br> <br>
	{% endif %}
	

	• views.py (in post add the following snippets)
	        message = "Movie '%s' added successfully!" % name
	        return render(request, "movies.html", {'message': message})
	
Step 4:  List the movies before add form.
      
	• views.py 
	return render(request, "movies.html", {'message': message, 'movies': get_movies()})
	
	def get_movies():
	    movies = Movie.objects.all()
	    return movies
	
	• movies.html
		{% if movies %}
		            {% for movie in movies %}
		            	<li> {{ movie.name }} </li>
		            {% endfor %}
	        {% else %}
	                No movies added so far. <br>
	        {% endif %}  <br>
	
Step 5:  Implement remove feature in GET method
	
	• movies.html
	<li> <a href="/movies/remove/?id={{ movie.pk }}"> [x] </a> {{ movie.name }} </li>
	
	• urls.py
	url(r'^movies/remove/$', movies_remove),
	
	• views.py 
	def movies_remove(request):
	    if request.method == 'GET':
	        movie_id = request.GET.get('id', None)
	        movie = Movie.objects.get(pk=movie_id)
	        movie.delete()
	        message = "Movie '%s' deleted successfully!" % movie.name
	        return render(request, "movies.html", {'message': message, 'movies': get_movies()})
	    return HttpResponse("Invalid Request")
	
	
Step 6:  Fix Integrity Issues, exceptions & validation
      
	• views.py 
	
	def movies(request):
	        if len(name.strip()) == 0:
	            message = "Please enter a movie  name"
	        elif len(name.strip()) < 3:
	            message = "Not enough words!"
	        else:
	            try:
	                Movie.objects.create(name=name)
	                message = "Movie '%s' added successfully!" % name
	            except IntegrityError:
	                message = "Movie '%s' already exists!" % name
	
	def movies_remove(request):
	        try:
	            movie = Movie.objects.get(pk=movie_id)
	            movie.delete()
	            message = "Movie '%s' deleted successfully!" % movie.name
	        except:
	            message = "Invalid Movie. Delete Failed!"
	

Step 7:  Use Django Forms instead of HTML Forms
      
	• forms.py 
	class MovieForm(forms.Form):
	    name = forms.CharField(required=False)
	
	• views.py 
	def movies(request):
		form = MovieForm(request.POST)
		        if form.is_valid():
		            data = form.cleaned_data
		            name = data['name']
	
	return render(request, "movies.html", {'message': message, 'movies': get_movies(), 'form': MovieForm()})
	
	def movies_remove(request):
	return render(request, "movies.html", {'message': message, 'movies': get_movies(), 'form': MovieForm()})
	
	• movies.html
        <form action="/movies/" method="post"> {% csrf_token %}
        	{{ form.as_table }}
            <input type="submit" value="Add">
        </form>


Step 8:   Use form validation instead of view

	• forms.py       
	    name = forms.CharField(required = True)
	
	    def clean_name(self):
	        name = self.cleaned_data['name']
	        if len(name) < 3:
	            raise forms.ValidationError("Not enough words!")
	        return name
	
	• views.py 
	        if form.is_valid():
	            data = form.cleaned_data
	            name = data['name']
	            try:
	                Movie.objects.create(name=name)
	                message = "Movie '%s' added successfully!" % name
	            except IntegrityError:
	                message = "Movie '%s' already exists!" % name
	        else:
	            message = "There are errors in the given input"
	
	
Step 9:  Implement Delete Confirmation & use Post

	• movies.html
		<li> <a href="/movies/remove/{{ movie.pk }}"> [x] </a> {{ movie.name }} </li>
	• urls.py
		url(r'^movies/remove/(?P<movie_id>\d+)/$', movies_remove),      

	• movies_delete_confirm.html
	
	        <form method="post"> {% csrf_token %}
	            Would you like to delete <b> {{ movie.name }} </b> ?
	            <input type="submit" value="Yep. Sure">
	        </form>
	
	
	• views.py 
	def movies_remove(request, movie_id):
		    if request.method == 'GET':
		        try:
		            movie = Movie.objects.get(pk=movie_id)
		        except:
		            message = "Invalid Movie. Delete Failed!"
		            return render(request, "movies.html", {'movies': get_movies(), 'message': message, 'form': MovieForm()})
		        return render(request, "movies_delete_confirm.html", {'movie':movie })
		    if request.method == 'POST':
		        try:
		            movie = Movie.objects.get(pk=movie_id)
		            movie.delete()
		            message = "Movie '%s' deleted successfully!" % movie.name
		        except:
		            message = "Invalid Movie. Delete Failed!"
		        return render(request, "movies.html", {'message': message, 'movies': get_movies(), 'form': MovieForm()})
		    return HttpResponse("Invalid Request")
		

Step 10:  Implement Edit option
     
	• movies.html
		<li> <a href="/movies/remove/{{ movie.pk }}"> [x] </a> {{ movie.name }} <a href="/movies/edit/{{ movie.pk }}/"> [edit] </a> </li>
	
	• urls.py 
		url(r'^movies/edit/(?P<movie_id>\d+)/$', movies_edit),
	
	• movies_edit.html
	        <form method="post"> {% csrf_token %}
		            {{ form.as_table }}
		            <input type="submit" value="Save">
	        </form>
	• views.py
	
	def movies_edit(request, movie_id):
	    if request.method == 'GET':
	        try:
	            movie = Movie.objects.get(pk=movie_id)
	            form = MovieForm(initial={'name': movie.name})
	        except:
	            message = "Invalid Movie. Edit Failed!"
	            return render(request, "movies.html", {'movies': get_movies(), 'message': message, 'form': MovieForm()})
	        return render(request, "movies_edit.html", {'form':form })
	    if request.method == 'POST':
	        form = MovieForm(request.POST)
	        if form.is_valid():
	            data = form.cleaned_data
	            movie = Movie.objects.get(pk=movie_id)
	            movie.name = data['name']
	            movie.save()
	            message = "Movie %s modified successfully!" % data['name']
	            form = MovieForm()
	        else:
	            message = "There are errors in the given input"
	        return render(request, "movies.html", {'message': message, 'movies': get_movies(), 'form': form})
	    return HttpResponse("Invalid Request")
	
	
Step 11:   Enable Admin
      
	• forms.py 
	class MovieForm(forms.ModelForm):
	#    name = forms.CharField(required = True)
	
	    class Meta:
	        model = Movie
	
	• admin.py 
	class MovieAdmin(admin.ModelAdmin):
	    form = MovieForm
	

admin.site.register(Movie, MovieAdmin)