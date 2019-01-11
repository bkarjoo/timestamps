# TODO define usecases
# can make lists in a database
# need to define the location of the database
import datetime
import sqlite3
import appdirs
import pickle
import os
import re
import textwrap
from backports.shutil_get_terminal_size import get_terminal_size
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
    conn.execute(create_table_script)

def create_item_table(conn):
    script = """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_time TEXT,
            description TEXT
        )
    """
    conn.execute(script)

def create_folder_table(conn):
    script = """
        CREATE TABLE IF NOT EXISTS folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folder TEXT,
            parent TEXT
        )
    """
    conn.execute(script)

def create_tag_table(conn):
    script = """
        CREATE TABLE IF NOT  EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag TEXT
        )
    """
    conn.execute(script)

def create_duedate_table(conn):
    script = """
        CREATE TABLE IF NOT EXISTS due_dates (
            item_id INTEGER,
            date_time TEXT
        )
    """
    conn.execute(script)

def create_item_folder_table(conn):
    script = """
        CREATE TABLE IF NOT EXISTS item_to_folder (
            item_id INTEGER,
            folder_id INTEGER
        )
    """
    conn.execute(script)

def create_item_tag_table(conn):
    script = """
        CREATE TABLE IF NOT EXISTS item_to_tag (
            item_id INTEGER,
            tag_id INTEGER
        )
    """



conn = get_db_connection(db_file)
create_list_table(conn)
create_item_table(conn)
create_folder_table(conn)
create_tag_table(conn)
create_duedate_table(conn)
create_item_folder_table(conn)
create_item_tag_table(conn)

current_list = []

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
    if len(current_list) == 0:
        print 'Nothing to delete'
        return
    print id
    item = current_list[(int(id)-1)]
    print "Delete {}. {}(y/n)?".format(id, item[1])
    answer = raw_input("")
    if answer != "y": return

    script = """
        DELETE FROM timestamps WHERE id = ?
    """
    cur = conn.cursor()

    cur.execute(script, (item[3], ))
    conn.commit()


def delete_tag(tag):
    script = """
        DELETE FROM timestamps WHERE tag = ?
    """
    cur = conn.cursor()
    cur.execute(script, (tag,))
    conn.commit()


def print_tags():
    script = """
        SELECT DISTINCT tag FROM timestamps order by tag
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
    global current_list
    current_list = items

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

# prints all the items with certain tag
def print_tag(tag):
    read_script = """
        SELECT date_time, description, tag, id FROM timestamps WHERE tag = ?
    """
    cur = conn.cursor()
    cur.execute(read_script, (tag,))

    items = cur.fetchall()
    global current_list
    current_list = items
    print '= = = = = = = = = = = = = = = = ='
    for i, item in enumerate(items):
        print (i+1), item[1]
    print '= = = = = = = done = = = = = = = ='

def clear_page():
    for i in range(100):
        print ''

def folder_exists(folder):
    script = "SELECT DISTINCT folder FROM folders WHERE folder=?"
    cur = conn.cursor()
    cur.execute(script, (folder,))
    items = cur.fetchall()
    return len(items) != 0

def make_folder(folder):
    if not folder_exists(folder):
        script = "INSERT INTO folders (folder, parent) VALUES (?,?);"
        cur = conn.cursor()
        cur.execute(script, (folder, current_folder))
        conn.commit()
        print "created folder {} in {}".format(folder, current_folder)
    else:
        print 'folder exists: ', folder

def print_folders():
    script = "SELECT folder, parent FROM folders WHERE parent = ? ORDER BY folder"
    cur = conn.cursor()
    cur.execute(script, (current_folder, ))
    items = cur.fetchall()

    for item in items:
        print item[0]

beginStr = '= = = = = = = = = = = = = = = = ='
endStr = '= = = = = = = done = = = = = = = ='

def render_par(text):
    lines = textwrap.wrap(text, get_terminal_size()[0])
    for line in lines:
        print line
    print ''

def print_help():
    print beginStr
    render_par('All commands must be preceded with a semi-colone: e.g. ;help')
    render_par('Line items are stored in the current folder. An item can only have one folder as its home. You can specify another folder to save an item to without navigating to that folder by preceding the folder name with @. If more than one folder is specified only the first one is considered. e.g. Enter this text. @some-folder')
    render_par('Similarly you can also add one or more tags to your items. Tags are preceeded with #. e.g. pick up some milk #todo #errand')
    print 'command\t\tdescription'
    print '-------\t\t----------------------------'
    print 'help\t\tprints this help file'
    print 'quit or q\tquits the program'
    print 'folder or f\tprints current folder'
    print endStr

def process_command(command):

    command = command[1:]

    if command == 'help':
        print_help()
    elif command == 'folder' or command == 'f':
        print 'Current folder is : ', current_folder


def insert_item(item):
    script = """
        INSERT INTO
    """

def write_item(item):
    folder = current_folder
    r = re.compile(r"([#])(\w+)\b")
    tags = r.findall(item)
    r = re.compile(r"([@])(\w+)\b")
    res = r.findall(item)
    if len(res) > 0:
        folder = r.findall(item)[0]
        folder = folder[1]
    # for the testing period new write items must be preceded by :
    item = item[1:]

    tags = [t[1] for t in tags]

    # strip the string from tags and folders
    item = item.replace(('@' + folder), '')
    for tag in tags:
        item = item.replace(('#' + tag), '')
    item = item.strip()
    item = (datetime.datetime.now(), item)

    write_item_script = """
        INSERT INTO items (date_time, description)
        VALUES (?, ?)
    """
    cur = conn.cursor()
    cur.execute(write_item_script, item)
    conn.commit()

    id = cur.execute('SELECT last_insert_rowid()').fetchone()[0]

    """
    INSERT INTO
    """



inStr = ''
current_tag = 'main'
current_folder = 'root'

while (True):
    inStr = raw_input()
    if inStr == ';quit' or inStr == ';q':
        break
    elif len(inStr) > 0 and inStr[0] == ';':
        process_command(inStr)
    elif len(inStr) > 0 and inStr[0] == ':':
        write_item(inStr)
    elif len(inStr) == 1 and inStr == 'p':
        print_tag(current_tag)
    elif len(inStr) == 2 and inStr == 'p*':
        print_all(current_tag)
    elif len(inStr) == 2 and inStr == 'cl':
        clear_page()
    elif len(inStr) > 1 and inStr[0] == ';': # focus tag
        write((datetime.datetime.now(), inStr[2:], 'focus'))
        print_all('focus')
    elif len(inStr) > 1 and inStr[0] == ':': # focus tag
        write((datetime.datetime.now(), inStr[2:], 'todo'))
    elif len(inStr) > 1 and inStr[0] == '/': # focus tag
        write((datetime.datetime.now(), inStr[2:], 'realization'))
    elif len(inStr) > 2 and inStr[:2] == 'd ':
        delete(inStr.split(' ')[1])
    elif len(inStr) > 3 and inStr[:3] == 'dt ':
        delete_tag(inStr.split(' ')[1])
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
        print_tag(requested_tag)
    elif len(inStr) > 4 and inStr[:4] == 'pt* ':
        requested_tag = inStr.split(' ')[1]
        print_all(requested_tag)
    elif len(inStr) == 2 and inStr == 'pp':  # print pause
        print_all(current_tag, True, True)
    elif len(inStr) == 2 and inStr == 'pf':  # print pause
        print_folders()
    elif len (inStr) > 3 and inStr[:3] == 'mf ':
        make_folder(inStr.split(' ')[1])
    else:
        write((datetime.datetime.now(), inStr, current_tag))
