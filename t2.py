import sqlite3
import chardet
import xlrd
import time

print(str(time.time()))
'''
connect = sqlite3.connect("conf.db")
cursor = connect.cursor()
t = cursor.execute("select * from user_info where id = '21'").fetchall()
print(t[0][2])
connect.commit()
cursor.close()
connect.close()
'''
