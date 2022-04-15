import os
from os.path import join

repo_dir = os.path.dirname(__file__)

net_dir = join(repo_dir, "bayesgraphs")
epsilon = 0.00000001

path_pid = join(repo_dir, "pid.txt")

log_dir = join(repo_dir, "shared_files")

path_ip_port_json = join(repo_dir, "ip_port.json")

path_temp_data_file = join(net_dir, "bn_data_temporary.csv")

os.makedirs(log_dir, exist_ok=True)