import multiprocessing

workers = multiprocessing.cpu_count()
bind = '0.0.0.0:5000'
reload = True
daemon = True