import os
from datetime import datetime

if not os.path.exists("logs"):
    os.makedirs("logs")
    os.makedirs("logs/gunicorn")

bind = "0.0.0.0:8001"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
reload = True
accesslog = f"./logs/gunicorn/access_{datetime.now().strftime('%Y-%m-%d_%H')}.log"
errorlog = f"./logs/gunicorn/error_{datetime.now().strftime('%Y-%m-%d_%H')}.log"
loglevel = "info"
pidfile = "./master.pid"
