wsgi_app = "parasite.wsgi"
workers = 4
threads = 40
bind = "127.0.0.1:24242"
accesslog = "server-access.log"
errorlog = "server-error.log"
loglevel = "debug"
capture_output = True
