from StringIO import StringIO
from DateTime import DateTime
from plone.subrequest import subrequest
from urllib import unquote

from ho.pisa import pisaDocument
from pyPdf import PdfFileWriter, PdfFileReader


from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class PrintView(BrowserView):
    _print_template = ViewPageTemplateFile("print.pt")

    def print_to_pdf(self):
        pdf = StringIO()
        charset = self.context.portal_properties.site_properties.default_charset


        pdf = StringIO()
        charset = self.context.portal_properties.site_properties.default_charset


        def fetch_resources(uri, rel):
            """
            Callback to allow pisa/reportlab to retrieve Images,Stylesheets, etc.
            `uri` is the href attribute from the html link element.
            `rel` gives a relative path, but it's not used here.

            """
            urltool = getToolByName(self.context, "portal_url")
            portal = urltool.getPortalObject()
            base = portal.absolute_url()
            if uri.startswith(base):
                response = subrequest(unquote(uri[len(base)+1:]))
                if response.status != 200:
                    return None
                try:
                    # stupid pisa doesn't let me send charset.
                    ctype,encoding = response.getHeader('content-type').split('charset=')
                    ctype = ctype.split(';')[0]
                    # pisa only likes ascii css
                    data = response.getBody().decode(encoding).encode('ascii',errors='ignore')

                except ValueError:
                    ctype = response.getHeader('content-type').split(';')[0]
                    data = response.getBody()

                data = data.encode("base64").replace("\n", "")
                data_uri = 'data:{0};base64,{1}'.format(ctype, data)
                return data_uri
            return uri


        html = StringIO(self._print_template(view=self).encode(charset))
        pisadoc = pisaDocument(html, pdf, raise_exception=True, link_callback=fetch_resources)
#        pisadoc = pisaDocument(html, pdf, raise_exception=True)
        assert pdf.len != 0, 'Pisa PDF generation returned empty PDF!'
        html.close()


        pdfcontent = pdf.getvalue()
        pdf.close()

        now = DateTime()
        nice_filename = '%s_%s' % (filename, now.strftime('%Y%m%d'))

        self.request.response.setHeader("Content-Disposition",
                                        "attachment; filename=%s.pdf" % 
                                         nice_filename)
        self.request.response.setHeader("Content-Type", "application/pdf")
        self.request.response.setHeader("Content-Length", len(pdfcontent))
        self.request.response.setHeader('Last-Modified', DateTime.rfc822(DateTime()))
        self.request.response.setHeader("Cache-Control", "no-store")
        self.request.response.setHeader("Pragma", "no-cache")
        self.request.response.write(pdfcontent)
        return pdfcontent
