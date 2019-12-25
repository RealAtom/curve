import re
import json
import binascii
import hashlib
from urllib import parse


# Procesar requests
class Request:
    def __init__(self, request):
        self._request = request
    
    @property
    def method(self):
        return self._request.splitlines()[0].split()[0]

    @property
    def http(self):
        return self._request.splitlines()[0].split()[2]
    
    @property
    def path(self):
        data = self._request.splitlines()[0].split()[1]
        data = data.split('?')[0]
        if data != '/':
            return data.rstrip('/')
        return data

    @property
    def paths(self):
        return self.path.split('/')

    @property
    def headers(self):
        return dict(x.split(': ') for x in self._request.split('\r\n\r\n')[0].strip().splitlines()[1:])

    @property
    def data_get(self):
        path = self._request.splitlines()[0].split()[1]
        data = path.split('?')
        try:
            return dict(parse.unquote_plus(y).split('=') for y in data[1].split('&'))
        except:
            return {}

    @property
    def data_post(self):
        data = self._request.splitlines()[-1]
        try:
            return dict(parse.unquote_plus(y).split('=') for y in data.split('&'))
        except:
            return {}
    
    @property
    def data_json(self):
        data = self._request.splitlines()[-1]
        try:
            return json.loads(data)
        except:
            return {}


# Procesar respuesta a requests
class Response:
    def __init__(self):
        self.data = []
        self.raw_data = []

    def not_found(self):
        self.send('404 Not Found', options = {
            'code': '404',
            'status': 'Not Found'
        })
    
    def bad_request(self):
        self.send('400 Bad Request', options = {
            'code': '400',
            'status': 'Bad Request'
        })
    
    def not_implemented(self):
        self.send('501 Not Implemented', options = {
            'code': '501',
            'status': 'Not Implemented'
        })
    

    def _build_header(self, body, options = None):
        builder = Response.HeaderBuilder(body)
        if options is not None:
            builder.parse(options)
        self.data.extend(builder.build())

    def send(self, body, options = {}):
        self._build_header(body, options)
        self.data.append(body)

    def send_json(self, body, options = {}):
        body = json.dumps(body)
        options['content-type'] = 'application/json'
        self._build_header(body, options)
        self.data.append(body)

    def send_raw(self, body, options = {}):
        self._build_header(body, options)
        self.raw_data.append(body)


    class HeaderBuilder:
        def __init__(self, body, code = '200', status = 'OK', content_type = 'text/plain'):
            self.body = body
            self.code = code
            self.status = status
            self.content_type = content_type
            self.content_length = len(body)
            self.headers = {}

            md5 = hashlib.md5()
            if isinstance(body, str):
                md5.update(body.encode())
            else:
                md5.update(body)
            self.etag = md5.hexdigest()
        
        def parse(self, data):
            if 'code' in data:
                self.code = data['code']
            if 'status' in data:
                self.status = data['status']
            if 'content-type' in data:
                self.content_type = data['content-type']
            if 'headers' in data:
                self.headers = data['headers']
        
        def build(self):
            data = []
            data.append('HTTP/1.1 {} {}'.format(self.code, self.status))
            data.append('\nContent-Type: {}'.format(self.content_type))
            data.append('\nContent-Length: {}'.format(self.content_length))
            data.append('\nETag: {}'.format(self.etag))
            for header in self.headers:
                data.append('\n{}: {}'.format(header, self.headers[header]))
            data.append('\nConnection: close\n\n')
            return data


# Definir web app
class Curve:
    def __init__(self):
        self.response = Response()
        self.routes = {}

    def set_request(self, request):
        self.request = Request(request)
    
    @property
    def responses(self):
        path = None
        for route in self.routes:
            if re.match(route + '$', self.request.path):
                path = route

        if path is not None:
            self.routes[path]()
        else:
            self.response.not_found()

        data = [x.encode() for x in self.response.data]
        data.extend(self.response.raw_data)

        self.response = Response()
        return data
    
    def route(self, action):
        def decorate(function):
            def wrapper(*args):
                self.routes[action] = function
            return wrapper
        return decorate

