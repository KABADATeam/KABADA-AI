import argparse
import os
from os.path import join
from config import repo_dir, path_pid
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument('command', type=str)
parser.add_argument('--ip', type=str, default="localhost")
parser.add_argument('--port', type=int, default=2222)
args = parser.parse_args()

flag_on_windows = sys.platform == 'win32'


def start():
    if os.path.exists(path_pid):
        print("Allready running")
        sys.exit(0)

    if flag_on_windows:
        cmd = ['python', join(repo_dir, "ai_rest_api.py"), f"--ip={args.ip}", f"--port={args.port}"]
    else:
        cmd = ['python3', join(repo_dir, "ai_rest_api.py"), f"--ip={args.ip}", f"--port={args.port}"]
    subprocess.Popen(cmd, shell=False, stdout=subprocess.DEVNULL)


def stop():
    try:
        with open(path_pid, "r") as conn:
            pid = int(conn.read())
            # print("read pid " + str(pid))
    except Exception as e:
        # print(e)
        print("AI server not Running? Couldn't find pid file")
        sys.exit(1)

    try:
        os.kill(pid, 1)
        os.remove(path_pid)
    except Exception as e:
        if not isinstance(e, SystemError):
            print(e)
            print("AI server already down?")
            sys.exit(1)


if args.command == "start":
    start()
elif args.command == "stop":
    stop()
elif args.command == "restart":
    stop()
    start()
else:
    print("wrong command")