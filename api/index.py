import os
from django.core.wsgi import get_wsgi_application
from django.core.management import execute_from_command_line
from http.server import BaseHTTPRequestHandler
from io import BytesIO

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'custommoviesite.settings')
application = get_wsgi_application()

# Define a handler class for Vercel to use
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Create a BytesIO buffer for capturing the response
        response = BytesIO()
        
        # Use Django's WSGI application to process the request
        environ = self.get_environ()
        response_body = application(environ, self.start_response)
        
        # Write the response
        response.write(response_body)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(response.getvalue())

    def get_environ(self):
        return {
            'REQUEST_METHOD': self.command,
            'PATH_INFO': self.path,
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '8000',
            'wsgi.input': BytesIO(self.rfile.read(int(self.headers.get('Content-Length', 0)))),
            'wsgi.errors': BytesIO(),
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'http',
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
        }

    def start_response(self, status, headers):
        self.send_response(int(status.split()[0]))
        for header in headers:
            self.send_header(header[0], header[1])
        self.end_headers()

# Create an instance of the handler
def handler(request):
    return Handler(request)
