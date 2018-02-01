# simple form usage in view
def my_view(request, template_name='home.html'):
    # sticks in a POST or renders an empty form
    form = MyForm(request.POST or None)
    if form.is_valid():
        do_something()
        return redirect('/')
    return render_to_response(template_name, {'form':form})

# form with files
def my_view(request, template_name='home.html'):
    form = MyForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        do_something()
        return redirect('/')
    return render_to_response(template_name, {'form':form})

# ModelForm usage
def my_model_edit(request, slug=slug, template_name='home.html'):
    mymodel = get_object_or_404(MyModel, slug=slug)
    form = MyModelForm(request.POST or None, instance=mymodel)
    if form.is_valid():
        mymodel = form.save()
        mymodel.edited_today = True
        mymodel.save()
        return redirect('/')
    return render_to_response(template_name, {
            'form':form,
            'mymodel':mymodel
            }
    )
