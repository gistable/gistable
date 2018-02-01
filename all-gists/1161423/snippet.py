from django.http import QueryDict
from django.http.multipartparser import MultiValueDict

class RESTMiddleware(object):
    def process_request(self,request):
        request.PUT=QueryDict('')
        request.DELETE = QueryDict('')
        method = request.META.get('REQUEST_METHOD','').upper() #upper ? rly?
        if method == 'PUT':
            self.handle_PUT(request)
        elif method == 'DELETE':
            self.handle_DELETE(request)

    def handle_DELETE(self,request):
        request.DELETE, request._files = self.parse_request(request)
    
    def handle_PUT(self,request):
        request.PUT,request._files  =   self.parse_request(request)
    
    def parse_request(self,request):
        if request.META.get('CONTENT_TYPE', '').startswith('multipart'):
            return self.parse_multipart(request)
        else:
            return (self.parse_form(request), MultiValueDict())
    
    def parse_form(self,request):
        return QueryDict(request.raw_post_data)
    
    def parse_multipart(self,request):
        return request.parse_file_upload(request.META,request)