# TODO define usecases
# can make lists in a database
# need to define the location of the database
import datetime
import sqlite3
import appdirs
import pickle
import os
appname = "TimeStamps"
appauthor = "BKar"

storage_path = appdirs.user_data_dir(appname, appauthor)
if not os.path.exists(storage_path):
    os.makedirs(storage_path)


# make an sqlite database
db_file = storage_path + '/timestamps.db'
print db_file

def get_db_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print e;

    return None


def create_list_table(conn):
    create_table_script = """
        CREATE TABLE IF NOT EXISTS timestamps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_time TEXT,
            description TEXT,
            tag TEXT
        )
    """
    conn.execute(create_table_script);


conn = get_db_connection(db_file)
create_list_table(conn)


def write(item):
    write_item_script = """
        INSERT INTO timestamps (date_time, description, tag)
        VALUES (?, ?, ?)
    """
    cur = conn.cursor()
    cur.execute(write_item_script, item)
    conn.commit()
    return cur.lastrowid


def delete(id):
    delete_item_script = """
        DELETE FROM timestamps WHERE id = ?
    """
    cur = conn.cursor()
    cur.execute(delete_item_script, (id, ))
    conn.commit()


def print_tags():
    script = """
        SELECT DISTINCT tag FROM timestamps
    """
    cur = conn.cursor()
    cur.execute(script)
    tags = cur.fetchall()
    print '= = = = = = = = = = = = = = = = ='
    for tag in tags:
        print tag[0]

def print_all(tag, item_only=False, pause=False):
    read_script = """
        SELECT date_time, description, tag, id FROM timestamps WHERE tag = ?
    """
    cur = conn.cursor()
    cur.execute(read_script, (tag,))

    items = cur.fetchall()


    elapsed_time_str = ''
    prev_id = prev_time = prev_text = elapsed_time = None
    print '= = = = = = = = = = = = = = = = ='
    for i, item in enumerate(items):

        if item_only:
            print item[1]
            if pause:
                inp = raw_input()
                if len(inp) == 1 and inp == 'b':
                    print '= = = = = = = done = = = = = = = ='
                    return
        else:
            timestamp = datetime.datetime.strptime(item[0],'%Y-%m-%d %H:%M:%S.%f')

            if (prev_time):
                elapsed_time = timestamp - prev_time
                elapsed_time_str = str(elapsed_time).split('.')[0]
                print "{} {} {} {}".format(
                    prev_id,
                    prev_time.strftime("%Y-%m-%d %H:%M:%S"),
                    str(elapsed_time).split('.')[0],
                    prev_text)

            if i == len(items) - 1:
                print "{} {} {} {}".format(
                    item[3],
                    timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    '0:00:00',
                    item[1])

            prev_id = item[3]
            prev_time = timestamp
            prev_text = item[1]

    print '= = = = = = = done = = = = = = = ='






inStr = ''
current_tag = 'main'

while (True):
    inStr = raw_input()

    if len(inStr) == 1 and inStr == 'q':
        break
    elif len(inStr) == 1 and inStr == 'p':
        print_all(current_tag, True)
    elif len(inStr) == 2 and inStr == 'p*':
        print_all(current_tag)
    elif len(inStr) > 1 and inStr[0] == ';': # focus tag
        write((datetime.datetime.now(), inStr[2:], 'focus'))
        print_all('focus')
    elif len(inStr) > 1 and inStr[0] == ':': # focus tag
        write((datetime.datetime.now(), inStr[2:], 'todo'))
    elif len(inStr) > 1 and inStr[0] == '/': # focus tag
        write((datetime.datetime.now(), inStr[2:], 'realization'))
    elif len(inStr) > 2 and inStr[:2] == 'd ':
        delete(inStr.split(' ')[1])
    elif len(inStr) == 1 and inStr == 't':
        print 'In tag: {}'.format(current_tag)
    elif len(inStr) > 2 and inStr[:2] == 't ':
        current_tag = inStr.split(' ')[1]
        print 'In tag: {}'.format(current_tag)
    elif len(inStr) == 2 and inStr == 'tm':
        current_tag = 'main'
        print 'In tag: {}'.format(current_tag)
    elif len(inStr) == 2 and inStr == 'pt':
        print_tags()
    elif len(inStr) == 2 and inStr == 'p;':
        print_all('focus')
    elif len(inStr) == 2 and inStr == 'p:':
        print_all('todo', True)
    elif len(inStr) == 2 and inStr == 'p/':
        print_all('realization', True)
    elif len(inStr) > 2 and inStr[:3] == 'pt ':
        requested_tag = inStr.split(' ')[1]
        print_all(requested_tag, True)
    elif len(inStr) > 4 and inStr[:4] == 'pt* ':
        requested_tag = inStr.split(' ')[1]
        print_all(requested_tag)
    elif len(inStr) == 2 and inStr == 'pp':  # print pause
        print_all(current_tag, True, True)
    else:
        write((datetime.datetime.now(), inStr, current_tag))
