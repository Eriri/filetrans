import tkinter
from tkinter import *
import socketserver
import os
import sys


def init_():
    work_dir = os.path.abspath()
    work_port = 8080
    tk = tkinter.Tk()
    return work_dir, work_port


def perpare_(work_dir, work_port):
    for item in os.listdir(work_dir):


def run_(sserver, work_dir):
    tk = tkinter.Tk()


if __name__ == "__main__":
    work_dir, work_port = init_()
    sserver = perpare_(work_dir, work_port)
    run_(sserver, work_dir, work_port)
