def GenericCSVExport(qs, fields=None):
    from django.db.models.loading import get_model
    from django.http import HttpResponse, HttpResponseForbidden
    from django.template.defaultfilters import slugify
    import csv
    
    model = qs.model
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % slugify(model.__name__)
    writer = csv.writer(response)
    if fields:
        headers = fields
    else:
        headers = []
        for field in model._meta.fields:
            headers.append(field.name)
    writer.writerow(headers)
    for obj in qs:
        row = []
        for field in headers:
            if field in headers:
                if '.' in field:
                    subfields = field.split('.')
                    val = obj
                    for subfield in subfields:
                        val = getattr(val, subfield)
                else:
                    val = getattr(obj, field)
                
                if callable(val):
                    val = val()
                row.append(val)
        writer.writerow(row)
    return response
