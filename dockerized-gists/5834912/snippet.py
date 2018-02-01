import mimerender

mimerender.register_mime('pdf', ('application/pdf',))
mimerender = mimerender.FlaskMimeRender(global_charset='UTF-8')

def render_pdf(html):
    from xhtml2pdf import pisa
    from cStringIO import StringIO
    pdf = StringIO()
    pisa.CreatePDF(StringIO(html.encode('utf-8')), pdf)
    resp = pdf.getvalue()
    pdf.close()
    return resp

@app.route('/invoice/<invoice_id>/', methods=['GET'])
@login_required
@mimerender(default='html', html=lambda html: html, pdf=render_pdf, override_input_key='format')
def view_invoice(org_id, invoice_id):
    html = render_template('invoice.html', id=invoice_id)
    return { 'html': html } # mimerender requires a dict
    