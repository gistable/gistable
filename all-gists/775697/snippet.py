@transaction.commit_on_success
def _action(action, o):
    getattr(o,action)()
    o.is_processing = False
    o.save()

def _bulk_action(action, objs):
    for o in objs:
        _action(action,o)


def bulk_action(request, t):

    ...
    objs = model.objects.filter(pk__in=pks)

    if request.method == 'POST':
        objs.update(is_processing=True)

        from multiprocessing import Process
        p = Process(target=_bulk_action,args=(action,objs))
        p.start()

        return HttpResponseRedirect(next_url)

    context = {'t': t, 'action': action, 'objs': objs, 'model': model}
    return render_to_response(...)