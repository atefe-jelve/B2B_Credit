
# gunicorn -c /path/to/your/project/gunicorn_config.py project.wsgi:application
# unicorn --bind 0.0.0.0:8000 config.wsgi
# gunicorn -c /home/atefeh/Desktop/seller_managment/gunicorn_config.py config.wsgi:application


import multiprocessing

bind = '0.0.0.0:8000'

workers = multiprocessing.cpu_count() * 2 + 1

threads = 3

worker_class = 'gthread'

timeout = 60

accesslog = '/var/log/gunicorn/access.log'
errorlog = '/home/atefeh/Desktop/seller_managment/gunicorn_error.log'

loglevel = 'error'

limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

proc_name = 'b2b_credit_gunicorn'

keepalive = 2

preload_app = False
