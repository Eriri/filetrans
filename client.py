from sql import *
from serverbase import *
import sys

server_port = 9090
proj_path = None

print(log_in("127.0.0.1", 8080, "21", "145b021e"))
ss = run_cs("127.0.0.1", 9090, sys.path[0])
