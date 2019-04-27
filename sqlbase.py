from sqlite3 import connect
from utilities import *


def select(connection, table, attributes, areas=None, values=None):
    attributes = ",".join(attributes)
    conditions = "" if areas is None else " where "+" and ".join([str(a) + "='" + str(v) + "'" for a, v in zip(areas, values)])
    return connection.execute("select "+attributes+" from "+table+conditions).fetchall()


def select_one(connection, table, attributes, areas=None, values=None):
    attributes = ",".join(attributes)
    conditions = "" if areas is None else " where "+" and ".join([str(a) + "='" + str(v) + "'" for a, v in zip(areas, values)])
    return connection.execute("select "+attributes+" from "+table+conditions).fetchone()


def insert(connection, table, areas, values):
    areas, values = ",".join(areas), ",".join(["'"+str(v)+"'" for v in values])
    connection.execute("insert or replace into "+table + "("+areas+")" + "values("+values+")")


def delete(connection, table, areas, values):
    conditions = " where "+" and ".join([str(a) + "='"+str(v)+"'" for a, v in zip(areas, values)])
    connection.execute("delete from "+table+conditions)


def update(connection, table, areas, values, careas, cvalues):
    attributes = ",".join([str(a) + "='"+str(v)+"'" for a, v in zip(areas, values)])
    conditions = " where "+" and ".join([str(a)+"="+("NULL" if v=="NULL" else "'"+str(v)+"'") for a,v in zip(careas,cvalues)])
    connection.execute("update "+table+" set "+attributes+conditions)


def initiate(path):
    database = os.path.join(path, DEFAULT_DATABASE)
    if not os.path.isfile(database):
        connection = connect(database)
        connection.execute(TABLE_USER)
        connection.execute(TABLE_PROBLEM)
        connection.execute(TABLE_TEST)
        connection.commit(), connection.close()
    return database


def import_user(database, no, name):
    connection = connect(database)
    insert(connection, "user", ["no", "name", ], [no, name])
    connection.commit(), connection.close()


def delete_user(database, nos):
    connection = connect(database)
    for no in nos:
        delete(connection, "user", ["no"], [no])
    connection.commit(), connection.close()

