def search(request):
  search_string=request.POST['search_string']
  if re.match(r'^\s*$',search_string): return redirect('home')
  results=[]
  search_fields=('id','name')
  equipment_models = \ 
      [model for model in django.db.models.get_models() if\ 
        model._meta.db_table.startswith("equipment_")]
  for model in equipment_models:
    query=halipsearch.get_query(search_string,search_fields)
    results+=(model.objects.filter(query))
  extra_context={'object_list':results,
    'pagetitle':"Search Results for '"+search_string+"'"}
  return render_to_response(
    'equipment/generic_list.html',
    extra_context,
    context_instance=RequestContext(request)
  )
