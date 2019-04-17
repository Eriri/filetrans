import sys
import os
import threading
import time
import multiprocessing
import threading
import socketserver
import wx
import xlrd


if __name__ == "__main__":
    item = [1,2]
    try:
        assert item[3] == 3
        print("?")
    except:
        print("ku")

    '''
    sheet = xlrd.open_workbook("d:/filetrans/信息.xlsx").sheets()[0]
    attributes = sheet.row_values(0)
    print(attributes.index("ibui"))'''


