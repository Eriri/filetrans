import sys
import sql
import serverbase
import os
import threading
import time
import multiprocessing
import threading


def a():
    print("a")


def b():
    print("b")


if __name__ == "__main__":
    '''p = multiprocessing.Pool()
    data = []
    for i in range(10):
        p.apply_async(func=a, args=(i,), callback=lambda x: data.append(x))
    p.close()
    p.join()
    print(data)'''
    b(), a()
