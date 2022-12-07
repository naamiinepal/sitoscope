wsgi_app = "parasite.wsgi"
workers = 1
threads = 80
bind = "127.0.0.1:23232"
accesslog = "server-access.log"
errorlog = "server-error.log"
loglevel = "debug"
capture_output = True
