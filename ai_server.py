import signal

from gevent.pywsgi import WSGIServer
from ai_rest_api import app
import argparse
import os
from os.path import join
from config import repo_dir
import subprocess
import sys
import atexit
from time import time, sleep
import logging


class Daemon:
    def __init__(self, args=None):
        self.pid_path = join(repo_dir, "pid.txt")
        self.args = args

    def daemonize(self):
        pid = os.fork()
        try:
            if pid > 0:
                sys.exit(0)
        except OSError as err:
            sys.stderr.write(f"fork #1 failed {err}\n")
            sys.exit(1)

        os.chdir("/")
        os.setsid()
        os.umask(0)

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as err:
            sys.stderr.write(f"fork #2 failed {err}\n")
            sys.exit(1)

        sys.stdout.flush()
        sys.stderr.flush()

        si = open(os.devnull, 'r')
        so = open(os.devnull, 'a+')
        se = open(os.devnull, 'a+')

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        atexit.register(self.delete_pid)
        pid = str(os.getpid())
        with open(self.pid_path, "w+") as conn:
            conn.write(pid + '\n')

    def delete_pid(self):
        os.remove(self.pid_path)

    def start(self):
        try:
            with open(self.pid_path, 'r') as conn:
                pid = int(conn.read().strip())
        except IOError:
            pid = None

        if pid:
            sys.stderr.write(f"pidfile {self.pid_path} allready exist. Checking if daemon already up \n")

            try:
                os.kill(pid, 0)
                sys.stderr.write(f"process {pid} allready up, stop before running again\n")
                sys.exit(1)
            except OSError:
                self.delete_pid()

        self.daemonize()
        self.launch_server()

    def launch_server(self):
        logging.info("Starting WSGI server")
        print(111111111111111)
        # http_server = WSGIServer((args.ip, args.port), app)
        # http_server.serve_forever()

    def stop(self):
        try:
            with open(self.pid_path, "r") as conn:
                pid = int(conn.read().strip())
        except IOError:
            pid = None

        if not pid:
            sys.stderr.write(f"pidfile {self.pid_path} doesn't exist, daemon not running?")
            return

        try:
            while True:
                os.kill(pid, signal.SIGTERM)
                sleep(0.1)
        except OSError as err:
            error = str(err.args)
            if error.find("No such process") > 0:
                if os.path.exists(self.pid_path):
                    os.remove(self.pid_path)
            else:
                logging.error("Daemon exception")
                sys.exit()

    def restart(self):
        self.stop()
        self.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('command', type=str)  # possible values start/stop/restart
    parser.add_argument('--ip', type=str, default="localhost")
    parser.add_argument('--port', type=int, default=2222)
    args = parser.parse_args()

    daemon = Daemon()
    if args.command == "start":
        daemon.start()
    elif args.command == "stop":
        daemon.stop()
    elif args.command == "restart":
        daemon.restart()
    else:
        print("wrong command")