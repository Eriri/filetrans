from serverbase import *
from sql import *
import sys
import threading
import wx
from wx import *

server_port = 8080
client_port = 9090
proj_path = None


if __name__ == "__main__":
    db_name = init_db(sys.path[0])
    import_user_from_xls(os.path.join(sys.path[0], "user_info.xls"), db_name)
    ss = run_ss("127.0.0.1", 8080, db_name)
