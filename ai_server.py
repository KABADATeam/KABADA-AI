from gevent.pywsgi import WSGIServer
from ai_rest_api import app
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--ip', type=str, default="localhost")
parser.add_argument('--port', type=int, default=2222)

args = parser.parse_args()

http_server = WSGIServer((args.ip, args.port), app)
http_server.serve_forever()