from tornado import (ioloop, web, httpserver, 
                     httpclient, gen, httputil, escape)
from bs4 import BeautifulSoup
class DefaultHandler(web.RequestHandler):
    def get(self):
        self.write(
        """
        <!DOCTYPE html>
        <html>
          <head>
            <title>Google Scholar Search Extractor</title>
          </head>
          <body>
            <b>Wellcome!</b> 
          </body>
        </html>
        """)
        
class GoogleScholarSearchHandler(web.RequestHandler):
   
    @web.asynchronous
    @gen.engine
    def get(self):
        client = httpclient.AsyncHTTPClient()
        q = self.get_argument('q')
        start = self.get_argument('start', '10')
        hl = self.get_argument('hl', 'en')
        callback = self.get_argument('cb', None)
        request_url = httputil.url_concat(
            r'http://scholar.google.com/scholar', 
            dict(q = q, start = start, hl = hl)
        )
        response = yield gen.Task(client.fetch, request_url)
        result = self.extract_info(response.body)
        
        
        #json_string = escape.json_encode([obj for obj in result])
        if callback is not None:
            self.set_header(r'Content-Type', r'text/javascript')
            self._write_jsonp(result, callback)
        else:
            self.set_header(r'Content-Type', r'application/json')
            self._write_json(result)
        self.finish()

    def _write_json(self, list_obj):
        self.write('[')
        for obj in list_obj:
            self.write(escape.json_encode(obj) + ',')
        self.write(']')

    def _write_jsonp(self, list_obj, callback):
        self.write(';' + callback + '(')
        self._write_json(list_obj)
        self.write(');')
        

    def extract_info(self, response_body):
        
        soup = BeautifulSoup(response_body)
        items = soup.select('.gs_r')
        
        #generator
        for item in items:
            search = dict()
            
            #title
            title_section = item.select('h3 > a')
            if len(title_section) > 0:
                section = title_section[0]
                title = section.get_text()
                href = section.attrs['href']
                search['title'] = title
                search['href'] = href
            
            #pdf
            pdf_section = item.select('.gs_ggs > a')
            if len(pdf_section) > 0:
                section = pdf_section[0]
                pdf = section.attrs['href']
                search['pdf'] = pdf
            
            #authors
            authors_section_a = item.select('.gs_a > a')
            authors = list()
            for author in authors_section_a:
                author_dict = dict()
                author_dict['author'] = author.get_text()
                url = u"http://scholar.google.com"
                author_dict['citations'] = url + author.attrs['href']
                authors.append(author_dict)
            authors_section_b = item.select('.gs_a')
            if len(authors_section_b) > 0:
                section = authors_section_b[0]
                section_text = section.get_text()
                names, conference, publisher = section_text.split(' - ')
                for author in names.split(','):
                    authors.append({'author':author})
                
                search['conference'] = conference
                search['publisher'] = publisher
            search['authors'] = authors
            
            #abstract
            abstract_section = item.select('.gs_rs')
            if len(abstract_section) > 0:
                section = abstract_section[0]
                search['abstract'] = section.get_text()

            #citation
            citation_section = item.select('.gs_fl > a')
            if len(authors_section_b) > 0:
                section = citation_section[0]
                citation_count = section.get_text().split(' ')[2]
                search['citations'] = citation_count
     
            yield search
        


application = web.Application([
    (r'/g', GoogleScholarSearchHandler),
    (r'/.*', DefaultHandler),
], debug = True)

if __name__ == "__main__":
    application.listen(8000)
    ioloop.IOLoop.instance().start()